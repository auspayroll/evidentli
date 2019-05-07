import uuid
from random import randint

from orm.model import Model
from orm.patient import Patient
from orm import omop
from . import utils


class Rondo(Model):
    _name = "rondo"
    _fields = { 'cohorts': str, 'matched_pairs': str, 'random': bool, 'name': str }

    def allocate_random_cohort(self, patient, force=False):
        # allocat random cohort to patient, deterministically based on _id
        patient_id = patient._id
        assert patient_id
        no_cohorts = len(self._cohort_list)
        if self._cohort_list:
            if not force and not patient.cohort or force:
                # cohort_no = int(hashlib.sha256(str(patient_id).encode("utf-8")).hexdigest(), 16) % no_cohorts
                cohort_no = randint(0, no_cohorts - 1)
                allocated_cohort = self._cohort_list[cohort_no]
                patient.cohort = allocated_cohort
                patient.save()
                return allocated_cohort

    def _reset_pair_ids(self):
        self._load_patients()
        for pat in self._patients:
            pat.cohort = ''
            pat.save()

    def allocate_random_cohorts(self):
        """set random cohorts for all patients, useful for testing"""
        self._patients = Patient.all(project_id=self._project_id)
        for patient in self._patients:
            self.allocate_random_cohort(patient, force=True)


    @property
    def patient_cohorts(self):
        self._load_patients()
        cohort_dict = {}
        for patient in self._patients:
            cohort_list = cohort_dict.setdefault(patient.cohort, [])
            cohort_list.append(patient)
        return cohort_dict

    @property
    def _cohort_list(self):
        return utils._split_string(self.cohorts)

    @property
    def _matched_pairs_dict(self):
        kw = {}
        if not self.matched_pairs:
            return kw

        keywords = utils._split_string(self.matched_pairs)
        keywords = list(dict.fromkeys(keywords))
        for keyword in keywords:
            try:
                table, field = keyword.split('.')
            except:
                pass
            else:
                table_fields = kw.setdefault(table.capitalize(),[])
                if field.lower() not in table_fields:
                    table_fields.append(field.lower())
        return kw

    @property
    def _matched_pair_list(self):
        l = []
        for k, vl in self._matched_pairs_dict.items():
            for v in vl:
                l.append("%s.%s" % (k,v))
        return l


    def _load_patients(self, limit=None):
        matched_pairs_dict = self._matched_pairs_dict
        if type(self._patients) is list:
            return self._patients
        else:
            patients = Patient.filter(project_id=self._project_id, 
                cohort=self._cohort_list, omop=list(matched_pairs_dict.keys()))

            cohort_counts = {}
            pats = []
            for patient in patients:
                #patient.pair_id = None
                if limit:
                    cohort_count = cohort_counts.setdefault(patient.cohort, 0)
                    if cohort_count < limit:
                        cohort_counts[patient.cohort] = cohort_count + 1
                        pats.append(patient)
                else:
                    pats.append(patient)
                #patient._field_updates.clear()

            self._patients = pats


    def match_patient(self, patient):
        self._load_patients()
        patient_pairs = []
        if patient.cohort not in self._cohort_list:
            return []

        if patient.pair_id:
            return [p for p in self._patients if p.pair_id == patient.pair_id and p._id != patient._id]

        match_pattern = {}
        for match_field in self._matched_pair_list:
            tablename, fieldname = match_field.split(".")
            try:
                match_pattern[match_field] = getattr(patient, "_%s" % tablename)[fieldname]
            except:
                return []
            else:
                if not match_pattern[match_field]:
                    return [] # one of the fields is None, so cant' match

        patient.pair_id = uuid.uuid4().hex

        for cohort, patient_cohort in self.patient_cohorts.items():
            if cohort == patient.cohort or not cohort:
                continue #if the same cohort
            # .. and find a patient match
            for patient_pair in patient_cohort:
                if patient_pair.pair_id:
                   continue
                broken_match = False
                for k,v in match_pattern.items():
                    try:
                        if getattr(patient, "_%s" % tablename)[fieldname] != getattr(patient_pair, "_%s" % tablename)[fieldname]:
                            broken_match = True
                            break
                    except:
                        broken_match = True
                        break

                if not broken_match:
                    patient_pair.pair_id = patient.pair_id
                    patient_pair.save()
                    patient_pairs.append(patient_pair)
                    if patient._field_updates:
                        patient.save()
                    break # match found for cohort, go the next one

        if 'pair_id' in patient._field_updates:
            patient.pair_id = None
            del patient._field_updates['pair_id']
        self.matched_patients = patient_pairs
        return self.matched_patients


    def match_patients(self):
        self._load_patients()
        matched_pairs_dict = self._matched_pairs_dict
        self._load_patients()
        for patient in self._patients:
            matched_patients = self.match_patient(patient)
        return self._patients


    def save(self):
        if 'matched_pairs' in self._field_updates:
            self.matched_pairs = ', '.join(self._matched_pair_list)

        if 'cohorts' in self._field_updates:
            self.cohorts = ', '.join(self._cohort_list)

        return super(Rondo, self).save()
