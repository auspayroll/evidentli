import unittest
import uuid
import os

import requests
from flask import Flask

from rondo.rondo_model import Rondo
from rondo.orm import Patient, omop




class TestRondo(unittest.TestCase):

    def setUp(self):
        self.project_id = 'test_rondo_integration'

    def tearDown(self):
        pass

    def test1(self):
        rondo = Rondo(project_id=self.project_id, cohorts='A,B', matched_pairs='Person.gender_concept_id')
        rondo._load_patients(limit=6)
        rondo.match_patients()
        for pair_id, matches in rondo.matched_patients.items():
        	assert matches[0]._Person['gender_concept_id'] == matches[0]._Person['gender_concept_id']
        	m1 = Patient.get(project_id=self.project_id, id=matches[0]._id)
        	m2 = Patient.get(project_id=self.project_id, id=matches[1]._id)
        	assert m1.pair_id == m2.pair_id

    def test2(self):
    	pass
        #assert(len(rondo._patients) == 40)
        #rondo._patients = [Patient.create(_id="1", pair_id='7',_project_id=self.project_id, cohort='A', _Person={'gender_concept_id': 'm'}), 
        #	Patient.create(_id="2", pair_id='3',_project_id=self.project_id, cohort='B', _Person={'gender_concept_id': 'm'})]

        #rondo.match_patients()
        #print(rondo.matched_patients)

        #rondo.allocate_random_cohorts()
        #rondo._reset_pair_ids()
        #rondo.match_patients()
        #import pdb
        #pdb.set_trace()
        #print(rondo.matched_patients)



if __name__ == '__main__':
    unittest.main()
