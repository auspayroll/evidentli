import uuid
from random import randint

from .orm.model import Model
from .orm.patient import Patient
from .orm import omop


class Rondo(Model):
    _name = "rondo"
    _fields = {'cohorts': list, 'matched_pairs': str, 'match_by_cohort': bool, 'name': str}

    def allocate_random_cohort(self, patient):
        # allocat random cohort to patient, deterministically based on _id
        patient_id = patient._id
        assert patient_id
        no_cohorts = len(self.cohorts)
        if self.cohorts and not patient.cohort:
            # cohort_no = int(hashlib.sha256(str(patient_id).encode("utf-8")).hexdigest(), 16) % no_cohorts
            cohort_no = randint(0, no_cohorts - 1)
            allocated_cohort = self.cohorts[cohort_no]
            patient.cohort = allocated_cohort
            patient.save()
            return allocated_cohort

    def allocate_random_cohorts(self):
        """set random cohorts for all patients, useful for testing"""
        patients = Patient.all(self._project_id)
        for patient in patients:
            self.allocate_random_cohort(patient)

    def _match_patient(self, patient, criteria_dict, pair_id):
        """
        private method to find matching patients and update with pair_id
        criteria_dict = { 'Person': ['field1', 'field2'], ...}
        """
        matched_patient_ids = omop.match_patient(patient._project_id, patient.person_id, criteria_dict)
        matched_patients = Patient.all_in(project_id=patient._project_id, field='person_id', values=matched_patient_ids)
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
                table_fields = kw.setdefault(table.lower(),[])
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

    def match_patient(self, patient):
        find_match = self._matched_pairs_dict
        if not find_match: 
            return []
        pair_id = uuid.uuid4().hex
        matched_patients = self._match_patient(patient, find_match, pair_id)
        return matched_patients

    def save(self):
        if 'matched_pairs' in self._field_updates:
            self.matched_pairs = ', '.join(self._matched_pair_list)

        if 'cohorts' in self._field_updates:
            self.cohorts = ', '.join(self._cohort_list)

        return super(Rondo, self).save()
