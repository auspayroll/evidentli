import unittest
import uuid
import os

import requests
from flask import Flask

from rondo.rondo_model import Rondo
from rondo.orm import Patient, omop
from config import PIANO_API
from rondo import app


def random():
    return uuid.uuid4().hex


class TestRondo(unittest.TestCase):

    project_id = "test_rondo_integration"

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()
        self.patients = []
        print("setting up")

    def tearDown(self):
        for patient in self.patients:
            patient.cohort = ''
            patient.pair_id = ''
            patient.save()

    def test_createConfig(self):
        # create and update Rondo configuration
        rondo = Rondo(project_id=self.project_id, cohorts="A, B, C, D")
        _id = rondo.save()
        rondo = Rondo.get(project_id=self.project_id, id=_id)
        self.assertEqual(len(rondo._cohort_list), 4)

        # reset config values
        rondo.cohorts = 'X, Y, Z, X'
        _id = rondo.save()
        self.assertEqual(len(rondo._cohort_list), 3)
        rondo.get(project_id=self.project_id, id=_id)
        self.assertEqual(len(rondo._cohort_list), 3)

    def test_random_cohort(self):
        cohorts = 'T, R, V, D'
        rondo = Rondo(project_id=self.project_id, cohorts=cohorts)
        patient = Patient.all(project_id=self.project_id)[0]
        patient.cohort = None
        patient.save()
        self.assertEqual(patient.cohort, None)
        rondo.allocate_random_cohort(patient)
        self.assertTrue(patient.cohort in rondo._cohort_list)

    def test_matchedPair(self):
        rondo = Rondo(project_id=self.project_id, cohorts='A,B', matched_pairs='Person.gender_concept_id')
        rondo._load_patients(limit=6)
        rondo.match_patients()
        for pair_id, matches in rondo.matched_patients.items():
            assert matches[0]._Person['gender_concept_id'] == matches[0]._Person['gender_concept_id']
            m1 = Patient.get(project_id=self.project_id, id=matches[0]._id)
            m2 = Patient.get(project_id=self.project_id, id=matches[1]._id)
            assert m1.pair_id == m2.pair_id

    def test_matchedPairSingle(self):
        rondo = Rondo(project_id=self.project_id, cohorts='A,B', matched_pairs='Person.gender_concept_id')
        rondo._patients = test_patients = Patient.filter(project_id=self.project_id, person_id=[1,2,3])
        patient1 = test_patients[0]
        patient2 = test_patients[1]
        patient3 = test_patients[2]
        self.patients = [patient1, patient2, patient3]
        patient1.cohort = 'A'
        patient2.cohort = 'B'
        patient3.cohort = 'B'
        patient1._Person = { 'gender_concept_id': 'male'}
        patient2._Person = { 'gender_concept_id': 'male'}
        patient3._Person = { 'gender_concept_id': 'female'}
        matches = rondo.match_patient(patient1)
        assert patient1.pair_id == patient2.pair_id

    
    def test_flowfile(self):
        cohorts = 'T, R, V, D'
        rondo = Rondo(project_id=self.project_id, cohorts=cohorts)
        rondo_id = rondo.save()
        patient1 = Patient.filter(project_id=self.project_id, person_id=1)[0]
        self.patients = [patient1]
        flowfile_url = "%s/projects/%s/rondo/%s/flowfile" % (app.config['HOST'], self.project_id, rondo_id)
        response = requests.post(flowfile_url, json=patient1._json)
        self.assertTrue(response.json()['cohort'] in rondo._cohort_list)
    


if __name__ == '__main__':
    unittest.main()
