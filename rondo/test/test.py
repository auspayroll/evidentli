from os import getenv
import requests
import unittest
from rondo.rondo_model import Rondo
from orm import Patient
from config import PIANO_API


DELETE_AUTH_KEY = getenv('DELETE_AUTH_KEY')
EUPHO_AUTH_KEY = getenv("EUPHO_AUTH_KEY", "eupho")
OBOE_AUTHKEY = getenv("OBOE_AUTH_KEY", "eobo")


class TestRondo(unittest.TestCase):

    project_id = "test_rondo_integration"
    project_id_api = "test_rondo_integration_api"
    patients = []

    @staticmethod
    def create_project(project_id, project, eupho=None):
        # create project
        url = "%s/projects/%s/projectdata" % (PIANO_API, project_id)
        requests.post(url, json=[project])

        # create eupho config
        if eupho:
            url = "%s/projects/%s/eupho" % (PIANO_API, project_id)
            requests.post(url, json=[eupho], headers={"EUPHO-AUTHKEY": EUPHO_AUTH_KEY})

            # set oboe role
            requests.put("%s/projects/%s/omop/role" % (PIANO_API, project_id), headers={"AUTHKEY": OBOE_AUTHKEY})

            # refresh documents (patients)
            r = requests.get("%s/projects/%s/patients/refresh" % (PIANO_API, project_id))
            if r.status_code == requests.codes.ok:
                return r.json()
        return []

    @staticmethod
    def delete_project(project_id):
        url = "%s/projects/%s" % (PIANO_API, project_id)
        requests.delete(url, headers={"AUTHKEY": DELETE_AUTH_KEY})

    @classmethod
    def setUpClass(cls):
        # delete/clear test project(s)
        cls.delete_project(cls.project_id_api)

        # create test project(s)
        project_id = cls.project_id_api
        cls.project = {
            "_id": project_id,
            "type": "omop",
        }
        cls.project_eupho = {
            "_id": project_id,
            "project_type": "patients",
            "db_version": "v2018_syn_00",
            "table_permissions": ["condition_occurrence", "death", "drug_exposure", "measurement", "observation",
                                  "person", "procedure_occurrence", "provider", "specimen", "visit_occurrence"],
            "oboe_role": "%s_role" % project_id
        }
        cls.patients = cls.create_project(project_id, cls.project, cls.project_eupho)

    @classmethod
    def tearDownClass(cls):
        # delete/clear test project(s)
        cls.delete_project(cls.project_id_api)

    def setUp(self):
        self.project_id = 'test_rondo_integration'
        patient_data = {
            "1": { "cohort": 'A', 'test_val': 7, 
                '_Person':{ 'test_field1': 5}, '_Measurement': { 'val_as_int': 45.6, 'val_as_int2': 45.6 }  }, 

            "2": { "cohort": 'B', 'test_val': 12, 
                '_Person':{ 'test_field1': 5}, '_Measurement': { 'val_as_int': 45.6, 'val_as_int2': 45.5 }  },

            "3": { "cohort": 'A', 'test_val': 10, 
                '_Person':{ 'test_field1': 3}, '_Measurement': { 'val_as_int': 94.7 }  },

            "4": { "cohort": None, 'test_val': 7, 
                '_Person':{ 'test_field1': 5}, '_Measurement': { 'val_as_int': 45.6 }  },

            "5": { "cohort": 'C', 'test_val': 12, 
                '_Person':{ 'test_field1': 5}, '_Measurement': { 'val_as_int': 45.6, 'val_as_int2': 45.5 }  },
        }

        self._patients = { k: Patient.create(_project_id=self.project_id, _id=k, **v) for k,v in patient_data.items() }

    def tearDown(self):
        pass

    def test_random_cohort(self):
        cohorts = 'T, R, V, D'
        rondo = Rondo(project_id=self.project_id, cohorts=cohorts)
        patient = self._patients["4"]
        self.assertEqual(patient.cohort, None)
        rondo.allocate_random_cohort(patient)
        self.assertTrue(patient.cohort in rondo._cohort_list)

    def test_matchedPair(self):
        rondo = Rondo(project_id=self.project_id, cohorts='A,B', matched_pairs='Person.test_field1')
        rondo._patients = list(self._patients.values())
        rondo.match_patients()
        assert self._patients.get("1").pair_id == self._patients.get("2").pair_id

    def test_matchedPairSingleField(self):
        rondo = Rondo(project_id=self.project_id, cohorts='A,B', matched_pairs='Person.test_field1')
        rondo._patients = list(self._patients.values())
        patient = self._patients["1"]
        matched_patients = rondo.match_patient(patient)
        matched_patient_ids = [int(mp._id) for mp in rondo.matched_patients]
        matched_patient_ids.sort()
        assert  matched_patient_ids == [2,5]

    def test_matchedPairMultipleField(self):
        rondo = Rondo(project_id=self.project_id, cohorts='A,B', matched_pairs='Person.test_field1, Measurement.val_as_int')
        rondo._patients = list(self._patients.values())
        patient = self._patients["1"]
        matched_patients = rondo.match_patient(patient)
        matched_patient_ids = [int(mp._id) for mp in rondo.matched_patients]
        matched_patient_ids.sort()
        assert  matched_patient_ids == [2,5]

    def test_matchedPairMultipleCohort(self):
        rondo = Rondo(project_id=self.project_id, cohorts='A,B,C', matched_pairs='Person.test_field1, Measurement.val_as_int')
        rondo._patients = list(self._patients.values())
        patient = self._patients["1"]
        matched_patients = rondo.match_patient(patient)
        assert len(matched_patients) == 2
        assert 'C' in [p.cohort for p in matched_patients]
        assert 'B' in [p.cohort for p in matched_patients]
        assert matched_patients[0].pair_id == matched_patients[1].pair_id == patient.pair_id

    def test_misMatch(self):
        rondo = Rondo(project_id=self.project_id, cohorts='A,B', 
            matched_pairs='Person.test_field1, Measurement.val_as_int, Measurement.val_as_int2')
        rondo._patients = list(self._patients.values())
        patient = self._patients["1"]
        matched_patients = rondo.match_patient(patient)
        assert len(matched_patients) == 0
 
    def test_misMatch2(self):
        rondo = Rondo(project_id=self.project_id, cohorts='A,B', 
            matched_pairs='Person.test_field1, NonExistentTable.val_as_int3')
        rondo._patients = list(self._patients.values())
        patient = self._patients["1"]
        matched_patients = rondo.match_patient(patient)
        assert len(matched_patients) == 0

    def test_misMatch3(self):
        rondo = Rondo(project_id=self.project_id, cohorts='A,B', 
            matched_pairs='Person.test_field1, Measurement.non_existent_field')
        rondo._patients = list(self._patients.values())
        patient = self._patients["1"]
        matched_patients = rondo.match_patient(patient)
        assert len(matched_patients) == 0

    def test_rondo_api_random_cohort(self):
        # create config
        url = "%s/projects/%s/rondo" % (PIANO_API, self.project_id_api)
        config_id = "rondo_config_1"
        config = {
            "_id": config_id,
            "cohorts": "excl, incl",
            "random": True,
            "name": "rand test",
            "matched_pairs": ""
        }
        requests.post(url, json=[config])

        # test api
        url = "%s/rondo/api/projects/%s/rondo/%s/flowfile" % (PIANO_API, self.project_id_api, config_id)
        patient = self.patients[0]
        patient["test_key"] = "test_val"
        r = requests.post(url, json=patient)
        self.assertEquals(r.status_code, requests.codes.ok)
        self.assertTrue(r.content)
        _json = r.json()
        for k, v in patient.iteritems():
            self.assertEquals(_json[k], v)

        self.assertTrue("cohort" in _json)
        self.assertTrue(_json["cohort"] in ["incl", "excl"])

    def test_rondo_api_matched_pair(self):
        # create config
        url = "%s/projects/%s/rondo" % (PIANO_API, self.project_id_api)
        config_id = "rondo_config_2"
        cohorts = ["A", "B"]
        config = {
            "_id": config_id,
            "cohorts": ", ".join(cohorts),
            "random": False,
            "name": "mp test",
            "matched_pairs": "Person.gender_source_value"
        }
        requests.post(url, json=[config])

        # assign 1000 patients to cohorts
        patients = []
        cohort_len = len(cohorts)
        for i in range(1000):
            patients.append({
                "_id": self.patients[i]["_id"],
                "person_id": self.patients[i]["person_id"],
                "cohort": cohorts[i % cohort_len]
            })
        requests.post("%s/projects/%s/patients" % (PIANO_API, self.project_id_api), json=patients)

        # test api
        url = "%s/rondo/api/projects/%s/rondo/%s/flowfile" % (PIANO_API, self.project_id_api, config_id)
        patient = patients[1]
        patient["test_key"] = "test_val"
        r = requests.post(url, json=patient)
        self.assertEquals(r.status_code, requests.codes.ok)
        self.assertTrue(r.content)
        _json = r.json()
        for k, v in patient.iteritems():
            self.assertEquals(_json[k], v)

        self.assertTrue("cohort" in _json)
        self.assertTrue(_json["cohort"] in ["A", "B", "C"])

        self.assertTrue("pair_id" in _json)
        self.assertTrue(_json["pair_id"])


if __name__ == '__main__':
    unittest.main()
