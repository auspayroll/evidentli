import hashlib
import uuid
import requests
import library 


class Rondo:
    def __init__(self, *args, **kwargs):
        self.project_id = kwargs.get('project_id')
        self.config_id = kwargs.get('config_id')
        self.cohorts = kwargs.get('cohorts')
        self.matched_pairs = kwargs.get('matched_pairs')
        self.match_by_cohort = False
        if self.config_id:
            self.load_config()

    def create(self):
        pass

    def save(self):
        pass

    def load_config(self):
        pass

    def get_all_patients(self):
        return library.get_all_patients(self.project_id)

    def get_patient(self, patient_id):
        return library.get_patient(self.project_id, patient_id)

    def allocate_random_cohort(self, patient):
        # allocat random cohort to patient, deterministically based on _id
        patient_id = patient.get("_id")
        if patient_id is None:
            return None
        no_cohorts = len(self.cohorts)
        if self.cohorts:
            cohort_no = int(hashlib.sha256(str(patient_id).encode("utf-8")).hexdigest(), 16) % no_cohorts
            allocated_cohort = self.cohorts[cohort_no]
            library.store_in_patient(self.project_id, patient_id, "cohort", allocated_cohort)

    def allocate_cohort(self, patient, cohort_name):
        """manually allocate a cohort name to a patient"""
        _id = patient.get("_id")
        library.store_in_patient(self.project_id, _id, "cohort", cohort_name)

    def allocate_random_cohorts(self):
        """set random cohorts for all patients, useful for testing"""
        patients = self.get_all_patients()
        for patient in patients:
            self.allocate_random_cohort(patient)

    def reset_cohorts(self): 
        """reset cohorts for all patients, useful for testing"""
        pass

    def reset_matched_pairs(self):
        """resset matched pars for all patients, useful for testing"""
        pass

    def match_patient(self, patient, matched_pairs=None, match_by_cohort=False):
        matched_pairs = matched_pairs or self.matched_pairs
        match_by_cohort = match_by_cohort or self.match_by_cohort
        total_matches = 0
        if not matched_pairs: return
        patient_cohort = patient.get('cohort')
        pair_id = uuid.uuid4().hex
        find_match = {}
        for field_match in matched_pairs:
            field_match_value = patient.get(field_match)
            if field_match_value is None: #patient has no field
                continue
            find_match[field_match] = field_match_value

        if match_by_cohort and patient_cohort: #find matching pair for each cohort
            for cohort in self.cohorts:
                if cohort == patient_cohort:
                    continue # query other cohorts
                find_match["cohort"] = cohort
                if library.match_patient(self.project_id, pair_id, find_match):
                    total_matches = total_matches + 1

        else: #find a matching pair amongst all patients
            if library.match_patient(self.project_id, pair_id, find_match):
                total_matches = total_matches + 1

        if total_matches:
            patient_id = patient.get('_id')
            library.store_in_patient(self.project_id, patient_id, 'pair_id', pair_id)
        else:
            pair_id = None

        return { "pair_id": pair_id, "total_matches": total_matches }



                                                                       