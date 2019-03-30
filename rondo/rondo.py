import hashlib
import uuid
import requests
from .orm.model import Model
from .orm.patient import Patient

class Rondo(Model):
    _name = "rondo"
    _fields = { 'cohorts': list, 'matched_pairs': list, 'match_by_cohort': bool } 

    def allocate_random_cohort(self, patient):
        # allocat random cohort to patient, deterministically based on _id
        patient_id = patient._id
        assert patient_id
        no_cohorts = len(self.cohorts)
        if self.cohorts:
            cohort_no = int(hashlib.sha256(str(patient_id).encode("utf-8")).hexdigest(), 16) % no_cohorts
            allocated_cohort = self.cohorts[cohort_no]
            patient.cohort = allocated_cohort
            patient.save()


    def allocate_random_cohorts(self):
        """set random cohorts for all patients, useful for testing"""
        patients = Patient.all(self._project_id)
        for patient in patients:
            self.allocate_random_cohort(patient)

    def _match_patient(self, patient, criteria, pair_id):
        """
        private method to find matching patients and update with pair_id
        """
        matched_patients = Patient.filter(project_id=patient._project_id, **criteria)
        if matched_patients:

            for matched_patient in matched_patients:
                if matched_patient._id == patient._id:
                    continue
                if not matched_patient.pair_id:
                    matched_patient.pair_id = pair_id
                    matched_patient.save()
                    if patient.pair_id != pair_id:
                        patient.pair_id = pair_id
                        patient.save()
                    return matched_patient

    def match_patient(self, patient, matched_pairs=None, match_by_cohort=False):
        matched_pairs = matched_pairs or self.matched_pairs
        match_by_cohort = match_by_cohort or self.match_by_cohort
        
        if not matched_pairs: return
        pair_id = uuid.uuid4().hex
        find_match = {}
        for field_match in matched_pairs:
            field_match_value = getattr(patient, field_match)
            if field_match_value is None: #patient has no field
                continue
            find_match[field_match] = field_match_value

        if match_by_cohort and patient.cohort and self.cohorts: 
            patient_matches = []
            #find matching pair for each cohort
            for cohort in self.cohorts:
                if cohort == patient.cohort:
                    continue # bypass patient cohort
                find_match["cohort"] = cohort
                matched_patient = self._match_patient(patient, find_match, pair_id)
                if matched_patient:
                    patient_matches.append(matched_patient)
            return patient_matches     
        else:
            matched_patient = self._match_patient(patient, find_match, pair_id)
            if matched_patient:
                return [matched_patient]
            else:
                return []                                                                   