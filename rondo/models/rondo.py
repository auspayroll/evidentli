import hashlib
import uuid
import requests
from .model import Model

class Rondo(Model):

    @classmethod
    def get_all_configs(cls, project_id):
        return api.get_configs(project_id, "rondo")

    def save(self):
        payload =  { "cohorts": self.cohorts, "matched_pairs": self.matched_pairs,
            "match_by_cohort": self.match_by_cohort }

        if self.config_id:
            payload["_id"] = self.config_id
        self.config_id = api.save_config(self.project_id, "rondo", payload)
        return self.config_id

    def fetch(self):
        if self.config_id and self.project_id:
            configs = api.get_config(self.project_id, "rondo", self.config_id)
            self.cohorts = configs.get('cohorts')
            self.matched_pairs = configs.get('matched_pairs')
            self.match_by_cohort = configs.get('match_by_cohort')


        if self._id and self.project_id:
            project_data = api.get_project_data(self._id)
            for k, v in project_data.items():
                setattr(self, k, v)
            self._field_updates.clear()

        else:
            raise Exception("_id or project_id not set")

    def allocate_random_cohort(self, patient):
        # allocat random cohort to patient, deterministically based on _id
        patient_id = patient.get("_id")
        if patient_id is None:
            return None
        no_cohorts = len(self.cohorts)
        if self.cohorts:
            cohort_no = int(hashlib.sha256(str(patient_id).encode("utf-8")).hexdigest(), 16) % no_cohorts
            allocated_cohort = self.cohorts[cohort_no]
            api.store_in_patient(self.project_id, patient_id, "cohort", allocated_cohort)
            patient['cohort'] = allocated_cohort

    def allocate_cohort(self, patient, cohort_name):
        """manually allocate a cohort name to a patient"""
        _id = patient.get("_id")
        api.store_in_patient(self.project_id, _id, "cohort", cohort_name)
        patient['cohort'] = allocated_cohort

    def allocate_random_cohorts(self):
        """set random cohorts for all patients, useful for testing"""
        patients = self.get_all_patients()
        for patient in patients:
            self.allocate_random_cohort(patient)

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
                if api.match_patient(self.project_id, pair_id, find_match):
                    total_matches = total_matches + 1

        else: #find a matching pair amongst all patients
            if api.match_patient(self.project_id, pair_id, find_match):
                total_matches = total_matches + 1

        if total_matches:
            patient_id = patient.get('_id')
            api.store_in_patient(self.project_id, patient_id, 'pair_id', pair_id)
        else:
            pair_id = None

        if pair_id:
            patient['pair_id'] = pair_id



                                                                       