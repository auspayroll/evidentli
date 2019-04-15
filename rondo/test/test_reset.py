import unittest
import uuid
import os

import requests
from flask import Flask

from rondo.rondo_model import Rondo
from rondo.orm import Patient, omop
from config import PIANO_API

RONDO_HOST = os.getenv("RONDO_HOST", "http://0.0.0.0:5012")
DELETE_AUTH_KEY = os.getenv('DELETE_AUTH_KEY')
EUPHO_AUTH_KEY = os.getenv("EUPHO_AUTH_KEY", "eupho")
OBOE_AUTHKEY = os.getenv("OBOE_AUTH_KEY", "eobo")


def random():
    return uuid.uuid4().hex


class TestRondo(unittest.TestCase):

    project_id = "test_rondo_integration"

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
            requests.get("%s/doxieve/api/projects/%s/documents/refresh" % (PIANO_API, project_id))

    @staticmethod
    def delete_project(project_id):
        url = "%s/projects/%s" % (PIANO_API, project_id)
        requests.delete(url, headers={"AUTHKEY": DELETE_AUTH_KEY})

    @classmethod
    def setUpClass(cls):
        # delete/clear test project(s)
        cls.delete_project(cls.project_id)

        # create test project(s)
        project_id = cls.project_id
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
        cls.create_project(project_id, cls.project, cls.project_eupho)

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    def tearDown(self):
        pass

    def test_createConfig(self):
        # create and update Rondo configuration
        assert True




if __name__ == '__main__':
    unittest.main()
