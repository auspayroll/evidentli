import unittest
from os import getenv

import numpy as np
import requests

from config import PIANO_API
from orm import Patient
from sumo.sumo_model import Sumo

DELETE_AUTH_KEY = getenv('DELETE_AUTH_KEY')
EUPHO_AUTH_KEY = getenv("EUPHO_AUTH_KEY", "eupho")
OBOE_AUTHKEY = getenv("OBOE_AUTH_KEY", "eobo")


class TestSumo(unittest.TestCase):
    project_id = "test_sumo_integration"
    project_id_api = "test_sumo_integration_api"
    project_patients = []

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
        cls.delete_project(cls.project_id)
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
        cls.project_patients = cls.create_project(project_id, cls.project, cls.project_eupho)

        cls.create_project(cls.project_id, {"_id": cls.project_id, "type": "omop"})

    @classmethod
    def tearDownClass(cls):
        # delete/clear test project(s)
        cls.delete_project(cls.project_id_api)

    def setUp(self):
        self.foa = "Person.day_of_birth"
        self.patients = {
            "1": { "cohort": 'A', "pair_id": '3454354WWWW', 'test_val': 7 }, 
            "2": { "cohort": 'B', "pair_id": '3454354WWWW', 'test_val': 12 },
            "3": { "cohort": 'A', "pair_id": '3454354XXXX', 'test_val': 10 },
            "4": { "cohort": 'B', "pair_id": '3454354XXXX', 'test_val': 6 },
        }

        self.sumo = sumo = Sumo.create(_project_id=self.project_id, _id="test", cohorts='A,B', foa=self.foa)
        sumo._patients = [ Patient.create(_project_id=self.project_id, _id=k, _Person={ self.foa.split('.')[1]: v['test_val']}, **v) for k,v in self.patients.items()]

    def tearDown(self):
        self.delete_project(self.project_id)

    def test_stats_mean(self):
        sumo = self.sumo
        sumo.analyse()
        predicted_mean_for_cohort_a = np.mean([pat['test_val'] for _id, pat in self.patients.items() if pat['cohort'] == 'A'])
        assert(predicted_mean_for_cohort_a == sumo.stats['cohorts']['A'][self.foa]['mean'])
        predicted_mean_for_cohort_b = np.mean([pat['test_val'] for _id, pat in self.patients.items() if pat['cohort'] == 'B'])
        assert(predicted_mean_for_cohort_b == sumo.stats['cohorts']['B'][self.foa]['mean'])

    def test_stats_std(self):
        sumo = self.sumo
        sumo.analyse()
        predicted_std_for_cohort_a = np.std([pat['test_val'] for _id, pat in self.patients.items() if pat['cohort'] == 'A'])
        assert(predicted_std_for_cohort_a == sumo.stats['cohorts']['A'][self.foa]['std'])
        predicted_std_for_cohort_b = np.std([pat['test_val'] for _id, pat in self.patients.items() if pat['cohort'] == 'B'])
        assert(predicted_std_for_cohort_b == sumo.stats['cohorts']['B'][self.foa]['std'])
    
    def test_stats_median(self):
        sumo = self.sumo
        sumo.analyse()
        predicted_median_for_cohort_a = np.median([pat['test_val'] for _id, pat in self.patients.items() if pat['cohort'] == 'A'])
        assert(predicted_median_for_cohort_a == sumo.stats['cohorts']['A'][self.foa]['median'])
        predicted_median_for_cohort_b = np.median([pat['test_val'] for _id, pat in self.patients.items() if pat['cohort'] == 'B'])
        assert(predicted_median_for_cohort_b == sumo.stats['cohorts']['B'][self.foa]['median'])
    
    def test_compare_cohorts_mean(self):
        self.sumo.analyse()
        cohort_stats = self.sumo.compare_cohorts('A', 'B')
        predicted_mean_for_cohort_a = np.mean([pat['test_val'] for _id, pat in self.patients.items() if pat['cohort'] == 'A'])
        predicted_mean_for_cohort_b = np.mean([pat['test_val'] for _id, pat in self.patients.items() if pat['cohort'] == 'B'])
        expected_mean_diff = abs(predicted_mean_for_cohort_a - predicted_mean_for_cohort_b)
        assert(abs(cohort_stats[self.foa]['mean']) == abs(expected_mean_diff))

    def test_compare_cohorts_std(self):
        self.sumo.analyse()
        cohort_stats = self.sumo.compare_cohorts('A', 'B')
        predicted_std_for_cohort_a = np.std([pat['test_val'] for _id, pat in self.patients.items() if pat['cohort'] == 'A'])
        predicted_std_for_cohort_b = np.std([pat['test_val'] for _id, pat in self.patients.items() if pat['cohort'] == 'B'])
        expected_std_diff = abs(predicted_std_for_cohort_a - predicted_std_for_cohort_b)
        assert(abs(cohort_stats[self.foa]['std']) == abs(expected_std_diff))

    def test_compare_cohorts_median(self):
        self.sumo.analyse()
        cohort_stats = self.sumo.compare_cohorts('A', 'B')
        predicted_median_for_cohort_a = np.median([pat['test_val'] for _id, pat in self.patients.items() if pat['cohort'] == 'A'])
        predicted_median_for_cohort_b = np.median([pat['test_val'] for _id, pat in self.patients.items() if pat['cohort'] == 'B'])
        expected_median_diff = abs(predicted_median_for_cohort_a - predicted_median_for_cohort_b)
        assert(abs(cohort_stats[self.foa]['median']) == abs(expected_median_diff))

    def test_matched_pair_stats_mean(self):
        self.sumo.analyse()
        cohort_stats = cs = self.sumo.compare_cohort_matched_pairs('A', 'B')
        values = [ 7 - 12, 10 - 6]
        mean = np.mean(values)
        assert(cs[self.foa]['mean'] == mean)
    
    def test_matched_pair_stats_std(self):
        self.sumo.analyse()
        cohort_stats = cs = self.sumo.compare_cohort_matched_pairs('A', 'B')
        values = [ 7 - 12, 10 - 6]
        std = np.std(values)
        assert(cs[self.foa]['std'] == std)

    def test_matched_pair_stats_median(self):
        self.sumo.analyse()
        cohort_stats = cs = self.sumo.compare_cohort_matched_pairs('A', 'B')
        values = [ 7 - 12, 10 - 6]
        median = np.median(values)
        assert(cs[self.foa]['median'] == median)

    def test_categories_numeric(self):
        sumo = self.sumo
        sumo.categories = '11,7'
        sumo.analyse()
        distribution = self.sumo.stats['distribution'][self.foa]["total"]
        assert [v for (k,v) in distribution if k == '< 7.0'][0] == 2
        assert [v for (k,v) in distribution if k == '> 11.0'][0] == 1
        assert [v for (k,v) in distribution if k == '<= 11.0'][0] == 1

    def test_odds_cateogries_nominal(self):
        patients = {
            "1": { "cohort": 'A', "pair_id": '3454354WWWW', 'test_val': 'A' }, 
            "2": { "cohort": 'B', "pair_id": '3454354WWWW', 'test_val': 'A' },
            "3": { "cohort": 'A', "pair_id": '3454354XXXX', 'test_val': 'B' },
            "4": { "cohort": 'B', "pair_id": '3454354XXXX', 'test_val': 'C' },
            "5": { "cohort": 'A', "pair_id": '', 'test_val': 'A' },
        }
        self.sumo._patients = [ Patient.create(_project_id=self.project_id, _id=k,
            _Person={ self.foa.split('.')[1]: v['test_val']}, **v) for k,v in patients.items()]
        self.sumo.analyse()
        distribution = self.sumo.stats['distribution'][self.foa]["total"]
        assert [v for (k,v) in distribution if k == 'A'][0] == 3
        assert [v for (k,v) in distribution if k == 'B'][0] == 1

    def test_odds_ratio_nominal(self):
        patients = {
            "1": { "cohort": 'A', "pair_id": '3454354WWWW', 'test_val': 'A' }, 
            "2": { "cohort": 'B', "pair_id": '3454354WWWW', 'test_val': 'A' },
            "3": { "cohort": 'A', "pair_id": '3454354XXXX', 'test_val': 'B' },
            "4": { "cohort": 'B', "pair_id": '3454354XXXX', 'test_val': 'C' },
            "5": { "cohort": 'A', "pair_id": '', 'test_val': 'A' },
        }
        self.sumo._patients = [ Patient.create(_project_id=self.project_id, _id=k,
            _Person={ self.foa.split('.')[1]: v['test_val']}, **v) for k,v in patients.items()]
        self.sumo.exposure_level = 'A'
        self.sumo.analyse()
        assert self.sumo.stats['comparison']["A - B"][self.foa]['OR'] == (2.0/3.0) / (1.0/2.0)

    def test_odds_ratio_numeric(self):
        patients = {
            "1": { "cohort": 'A', "pair_id": '3454354WWWW', 'test_val': 1 }, 
            "2": { "cohort": 'B', "pair_id": '3454354WWWW', 'test_val': 5 },
            "3": { "cohort": 'A', "pair_id": '3454354XXXX', 'test_val': 7 },
            "4": { "cohort": 'B', "pair_id": '3454354XXXX', 'test_val': 1.2 },
            "5": { "cohort": 'A', "pair_id": '', 'test_val': 5 },
        }
        self.sumo._patients = [ Patient.create(_project_id=self.project_id, _id=k,
            _Person={ self.foa.split('.')[1]: v['test_val']}, **v) for k,v in patients.items()]
        self.sumo.exposure_level = 3
        self.sumo.analyse()
        assert self.sumo.stats['comparison']["A - B"][self.foa]['OR'] == (2.0/3.0) / (1.0/2.0)

    def test_sumo_api(self):
        # create config
        url = "%s/projects/%s/sumo" % (PIANO_API, self.project_id_api)
        config_id = "sumo_config_1"
        cohorts = ["A", "B"]
        config = {
            "_id": config_id,
            "name": "",
            "cohorts": ", ".join(cohorts),
            "exposure_level": "french",
            "foa": "Person.ethnicity_source_value",
            "categories": ""
        }
        requests.post(url, json=[config])

        # assign patients to cohorts
        patients = []
        cohort_len = len(cohorts)
        _range = 1000
        if len(self.project_patients) < _range:
            _range = len(self.project_patients)
        for i in range(_range):
            patients.append({
                "_id": self.project_patients[i]["_id"],
                "cohort": cohorts[i % cohort_len]
            })
        requests.post("%s/projects/%s/patients" % (PIANO_API, self.project_id_api), json=patients)

        # test api
        url = "%s/sumo/api/projects/%s/sumo/%s/calc_stats" % (PIANO_API, self.project_id_api, config_id)
        r = requests.get(url)
        self.assertEquals(r.status_code, requests.codes.ok)
        self.assertTrue(r.content)
        _json = r.json()

        self.assertTrue("distribution" in _json)
        self.assertTrue("fields" in _json)


if __name__ == '__main__':
    unittest.main()
