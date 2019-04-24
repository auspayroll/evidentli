import unittest
from orm import Patient, omop
from sumo.sumo_model import Sumo
import numpy as np


class TestSumo(unittest.TestCase):

    def setUp(self):
        self.project_id = 'test_rondo_integration'
        self.foa = "Person__day_of_birth"
        self.patients = {
            "1": { "cohort": 'A', "pair_id": '3454354WWWW', 'test_val': 7 }, 
            "2": { "cohort": 'B', "pair_id": '3454354WWWW', 'test_val': 12 },
            "3": { "cohort": 'A', "pair_id": '3454354XXXX', 'test_val': 10 },
            "4": { "cohort": 'B', "pair_id": '3454354XXXX', 'test_val': 6 },
        }

        self.sumo = sumo = Sumo(project_id=self.project_id, cohorts='A,B', foa=self.foa)
        sumo._patients = [ Patient.create(_project_id=self.project_id, _id=k, _Person={ self.foa.split('__')[1]: v['test_val']}, **v) for k,v in self.patients.items()]
        

    def tearDown(self):
        pass

    
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

    def test_compare_cohorts_mean(self):
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
        category_list = self.sumo.stats['categorized'][self.foa]
        assert [v for (k,v) in category_list if k == '< 7.0'][0] == 2
        assert [v for (k,v) in category_list if k == '> 11.0'][0] == 1
        assert [v for (k,v) in category_list if k == '<= 11.0'][0] == 1


    def test_odds_cateogries_nominal(self):
        patients = {
            "1": { "cohort": 'A', "pair_id": '3454354WWWW', 'test_val': 'A' }, 
            "2": { "cohort": 'B', "pair_id": '3454354WWWW', 'test_val': 'A' },
            "3": { "cohort": 'A', "pair_id": '3454354XXXX', 'test_val': 'B' },
            "4": { "cohort": 'B', "pair_id": '3454354XXXX', 'test_val': 'C' },
            "5": { "cohort": 'A', "pair_id": '', 'test_val': 'A' },
        }
        self.sumo._patients = [ Patient.create(_project_id=self.project_id, _id=k,
            _Person={ self.foa.split('__')[1]: v['test_val']}, **v) for k,v in patients.items()]
        self.sumo.analyse()
        category_list = self.sumo.stats['categorized'][self.foa]
        assert [v for (k,v) in category_list if k == 'A'][0] == 3
        assert [v for (k,v) in category_list if k == 'B'][0] == 1

    def test_odds_ratio_nominal(self):
        patients = {
            "1": { "cohort": 'A', "pair_id": '3454354WWWW', 'test_val': 'A' }, 
            "2": { "cohort": 'B', "pair_id": '3454354WWWW', 'test_val': 'A' },
            "3": { "cohort": 'A', "pair_id": '3454354XXXX', 'test_val': 'B' },
            "4": { "cohort": 'B', "pair_id": '3454354XXXX', 'test_val': 'C' },
            "5": { "cohort": 'A', "pair_id": '', 'test_val': 'A' },
        }
        self.sumo._patients = [ Patient.create(_project_id=self.project_id, _id=k,
            _Person={ self.foa.split('__')[1]: v['test_val']}, **v) for k,v in patients.items()]
        self.sumo.exposure_level = 'A'
        self.sumo.analyse()
        assert self.sumo.stats['comparison'][self.foa]['OR'] == (2/3) / (1/2)

     
    def test_odds_ratio_numeric(self):
        patients = {
            "1": { "cohort": 'A', "pair_id": '3454354WWWW', 'test_val': 1 }, 
            "2": { "cohort": 'B', "pair_id": '3454354WWWW', 'test_val': 5 },
            "3": { "cohort": 'A', "pair_id": '3454354XXXX', 'test_val': 7 },
            "4": { "cohort": 'B', "pair_id": '3454354XXXX', 'test_val': 1.2 },
            "5": { "cohort": 'A', "pair_id": '', 'test_val': 5 },
        }
        self.sumo._patients = [ Patient.create(_project_id=self.project_id, _id=k,
            _Person={ self.foa.split('__')[1]: v['test_val']}, **v) for k,v in patients.items()]
        self.sumo.exposure_level = 3
        self.sumo.analyse()
        assert self.sumo.stats['comparison'][self.foa]['OR'] == (2/3) / (1/2)

if __name__ == '__main__':
    unittest.main()
