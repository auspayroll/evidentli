import unittest
import uuid
import os

import requests
from flask import Flask

from rondo.rondo_model import Rondo
from rondo.orm import Patient, omop




class TestRondo(unittest.TestCase):

    def setUp(self):
        self.project_id = 'test_michael2'

    def tearDown(self):
        pass

    def test1(self):
        # create and update Rondo configuration

        #results = omop.get_omop(self.project_id, 'person', select=None, where=None, order_by=None, as_list=False, reidentify=False)
        #print(results)
        patient = Patient.filter(project_id='test_michael2', person_id=2)[0]
        print(patient.__dict__)
        #results = omop.get_omop(self.project_id, 'person', select=None, where='provider_id=4', order_by=None, as_list=False, reidentify=False)
        #print(len(results))
        rondo = Rondo(project_id=self.project_id, matched_pairs='Person.provider_id')
        matched_ids = rondo.match_patient(patient)
        print(matched_ids)



if __name__ == '__main__':
    unittest.main()
