import uuid
from random import randint

from .orm.model import Model
from .orm.patient import Patient
from .orm import omop


class Rondo(Model):
    _name = "rondo"
    _fields = { 'cohorts': str, 'matched_pairs': str, 'match_by_cohort': bool, 'name': str }

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

        
    def _match_patient(self, patient, criteria_dict, pair_id):
        """
        deprecated
        private method to find matching patients and update with pair_id
        criteria_dict = { 'Person': ['field1', 'field2'], ...}
        """
        matched_patient_ids = omop.match_patient(patient._project_id, patient.person_id, criteria_dict)
        matched_patients = Patient.filter(project_id=patient._project_id, person_id=matched_patient_ids, omop='Person')
        matched_cohorts = [patient.cohort]
        matched_patient_list = []
        if matched_patients:
            for matched_patient in matched_patients:
                if matched_patient._id == patient._id:
                    continue
                if not matched_patient.pair_id: #skip if already paired
                    matched_patient.pair_id = pair_id
                    if self.match_by_cohort and matched_patient.cohort not in matched_cohorts:
                        matched_cohorts.append(matched_patient.cohort)
                    matched_patient.save()
                    matched_patient_list.append(matched_patient)
                    if patient.pair_id != pair_id:
                        patient.pair_id = pair_id
                        patient.save()
                    if not self.match_by_cohort: 
                        # there are no cohorts, so return only one match
                        return matched_patient_list
        return matched_patient_list

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
        split_on = ','
        if split_on not in self.cohorts:
            split_on = ' '
        keywords = [x.strip() for x in self.cohorts.split(split_on)]
        cohort_list = list(dict.fromkeys(keywords))
        return cohort_list

    @property
    def _matched_pairs_dict(self):
        kw = {}
        if not self.matched_pairs:
            return kw

        split_on = ','
        if split_on not in self.matched_pairs:
            split_on = ' '
            
        keywords = [x.strip() for x in self.matched_pairs.split(split_on)]

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

    """
    deprecated
    def match_patient(self, patient):
        find_match = self._matched_pairs_dict
        if not find_match: 
            return []
        pair_id = uuid.uuid4().hex
        matched_patients = self._match_patient(patient, find_match, pair_id)
        return matched_patients
    """
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
            if cohort == patient.cohort:
                continue
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
                    break # match found for cohort

        if 'pair_id' in patient._field_updates:
            patient.pair_id = None
            del patient._field_updates['pair_id']
        return patient_pairs

    @property
    def matched_patients(self):
        self._load_patients()
        for patient in self._patients:
            patient.pair_id = None
            patient._field_updates.clear()
        if not self._patients:
            return None
        mpd = {}
        for pat in self._patients:
            if pat.pair_id:
                mpl = mpd.setdefault(pat.pair_id, [])
                mpl.append(pat)
        return mpd

    def match_patients(self):
        #import pdb
        #pdb.set_trace()
        matched_pairs_dict = self._matched_pairs_dict
        self._load_patients()
        for patient in self._patients:
            self.match_patient(patient)
        return self._patients


    def save(self):
        if 'matched_pairs' in self._field_updates:
            self.matched_pairs = ', '.join(self._matched_pair_list)

        if 'cohorts' in self._field_updates:
            self.cohorts = ', '.join(self._cohort_list)

        return super(Rondo, self).save()
