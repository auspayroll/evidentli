import unittest
from rondo.config import Rondo
from rondo.models import Patient
import pdb



class TestRondo(unittest.TestCase):

    def setUp(self):
        self.project_id = 'test_michael2'


    def tearDown(self):
        pass

    def test_createConfig(self):
        # create and update Rondo configuration
        rondo = Rondo(project_id=self.project_id, cohorts=['A','B','C','D'], matched_pairs=['age', 'height'])
        _id = rondo.save()
        rondo = Rondo(project_id=self.project_id, config_id=_id)
        rondo.load()
        self.assertEqual(len(rondo.cohorts), 4)
        self.assertEqual(len(rondo.matched_pairs), 2)

        #reset config values
        rondo.cohorts = ['X', 'Y', 'Z']
        rondo.matched_pairs = ['age']
        rondo.save()
        self.assertEqual(len(rondo.cohorts), 3)
        self.assertEqual(len(rondo.matched_pairs), 1)
        rondo.load()
        self.assertEqual(len(rondo.cohorts), 3)
        self.assertEqual(len(rondo.matched_pairs), 1)

    def test_cohort(self):
        rondo = Rondo(project_id=self.project_id, cohorts=['A','B','C','D'], matched_pairs=['age', 'height'])
        _id = rondo.save()
        patients = rondo.get_all_patients()

        #for patient in patients:
        #    rondo.allocate_random_cohort(patient)

    def test_matchedPair(self):
        pass

    def test_unmatchedPair(self):
        pass

    def test_matchedPairCohort(self):
        pass

    def test_unmatchedPairCohort(self):
        pass

if __name__ == '__main__':
    unittest.main()
