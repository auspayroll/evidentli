import unittest
from rondo.rondo_model import Rondo
from orm import Patient


class TestRondo(unittest.TestCase):

    project_id = "test_rondo_integration"

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
        assert matched_patients[0]._id == '2'

    def test_matchedPairMultipleField(self):
        rondo = Rondo(project_id=self.project_id, cohorts='A,B', matched_pairs='Person.test_field1, Measurement.val_as_int')
        rondo._patients = list(self._patients.values())
        patient = self._patients["1"]
        matched_patients = rondo.match_patient(patient)
        assert matched_patients[0]._id == '2'

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

    def test_misMatch2(self):
        rondo = Rondo(project_id=self.project_id, cohorts='A,B', 
            matched_pairs='Person.test_field1, Measurement.non_existent_field')
        rondo._patients = list(self._patients.values())
        patient = self._patients["1"]
        matched_patients = rondo.match_patient(patient)
        assert len(matched_patients) == 0


if __name__ == '__main__':
    unittest.main()
