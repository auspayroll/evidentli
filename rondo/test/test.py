import unittest
import uuid
import os

import requests
from flask import Flask

from rondo.rondo_model import Rondo
from rondo.orm import Patient

RONDO_HOST = os.getenv("RONDO_HOST", "http://0.0.0.0:5012")


def random():
    return uuid.uuid4().hex


class TestRondo(unittest.TestCase):

    def setUp(self):
        self.project_id = 'test_michael2'
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    def tearDown(self):
        pass

    def test_createConfig(self):
        # create and update Rondo configuration
        rondo = Rondo(project_id=self.project_id, cohorts=['A', 'B', 'C', 'D'],
                      matched_pairs=['age', 'height'])
        _id = rondo.save()
        rondo = Rondo.get(project_id=self.project_id, id=_id)
        self.assertEqual(len(rondo.cohorts), 4)
        self.assertEqual(len(rondo.matched_pairs), 2)

        # reset config values
        rondo.cohorts = ['X', 'Y', 'Z']
        rondo.matched_pairs = ['age']
        _id = rondo.save()
        self.assertEqual(len(rondo.cohorts), 3)
        self.assertEqual(len(rondo.matched_pairs), 1)
        rondo.get(project_id=self.project_id, id=_id)
        self.assertEqual(len(rondo.cohorts), 3)
        self.assertEqual(len(rondo.matched_pairs), 1)

    def test_random_cohort(self):
        cohorts = ['T', 'R', 'V', 'D']
        rondo = Rondo(project_id=self.project_id, cohorts=cohorts)
        patient = Patient.all(project_id=self.project_id)[0]
        patient.cohort = None
        patient.save()
        self.assertEqual(patient.cohort, None)
        rondo.allocate_random_cohort(patient)
        self.assertTrue(patient.cohort in cohorts)

    def test_matchedPair(self):
        test_val1 = random()
        test_val2 = random()
        patient1 = Patient(project_id=self.project_id, person_id=1,
                           test_field=test_val1, test_field2=test_val2)
        patient1.save()
        patient2 = Patient(project_id=self.project_id, person_id=2,
                           test_field=test_val1, test_field2=test_val2)
        patient2.save()

        rondo = Rondo(project_id=self.project_id,
                      matched_pairs=['test_field', 'test_field2'])
        rondo.save()
        matched_patients = rondo.match_patient(patient1)
        # print(matched_patients[0].__dict__)
        self.assertEqual(len(matched_patients), 1)
        matched_patient = matched_patients[0]
        self.assertEqual(matched_patient.pair_id, patient1.pair_id)

        # test for an unmatched patient
        patient3 = Patient(project_id=self.project_id, person_id=3,
                           test_field=test_val1, test_field2=test_val2)
        patient3.save()
        matched_patients = rondo.match_patient(patient3)
        # should be unmatched because current matched fields already have a pair_id 
        self.assertEqual(matched_patients, [])

    def test_matchedPairCohort(self):
        # we want to match pairs that are in different cohorts, ie don't 
        # match pairs that are in the same cohort
        cohort1 = random()
        cohort2 = random()
        test_val1 = random()
        test_val2 = random()
        patient1 = Patient(project_id=self.project_id, person_id=1,
                           test_field=test_val1, test_field2=test_val2)
        patient1.cohort = cohort1
        patient1.save()
        patient2 = Patient(project_id=self.project_id, person_id=2,
                           test_field=test_val1, test_field2=test_val2)
        patient2.cohort = cohort1
        patient2.save()

        # create rondo with match_by_cohort = True.
        rondo = Rondo(project_id=self.project_id,
                      matched_pairs=['test_field', 'test_field2'],
                      cohorts=[cohort1, cohort2], match_by_cohort=True)

        matched_patients = rondo.match_patient(patient1)
        # there should be no matched patients as
        self.assertEqual(matched_patients, [])

        # try putting patient 2 in a different cohort, and it should match
        patient2.cohort = cohort2
        patient2.save()
        matched_patients = rondo.match_patient(patient1)
        # should match patient 2
        self.assertEqual(patient2._id, matched_patients[0]._id)
        # the returned matched patient should have the same pair id
        self.assertEqual(patient1.pair_id, matched_patients[0].pair_id)

        # we'll add another patient in a different cohort, just to make sure
        cohort3 = random()
        # we need to update rondo to include the new cohort to search
        rondo.cohorts = [cohort1, cohort2, cohort3]
        # and reset patient 2 cohort, pair_id , note patient 2 is now stale
        patient2 = matched_patients[0]
        patient2.pair_id = None
        patient2.save()

        patient3 = Patient(project_id=self.project_id, person_id=3,
                           test_field=test_val1, test_field2=test_val2, cohort=cohort3)
        patient3.save()
        matched_patients = rondo.match_patient(patient1)
        # should match on patient 2 and patient 3
        self.assertEqual(len(matched_patients), 2)


    def test_flowfile(self):
        cohorts = ['T', 'R', 'V', 'D']
        rondo = Rondo(project_id=self.project_id, cohorts=cohorts)
        rondo_id = rondo.save()
        patient1 = Patient(project_id=self.project_id, person_id=1, firstname="testflowfile")
        patient1.save()
        flowfile_url = "%s/projects/%s/rondo/%s/flowfile" % (RONDO_HOST, self.project_id, rondo_id)
        print(patient1._json)
        response = requests.post(flowfile_url, json=patient1._json)
        self.assertTrue(response.json()['cohort'] in cohorts)


if __name__ == '__main__':
    unittest.main()
