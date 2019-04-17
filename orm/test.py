import unittest
import uuid
from orm.patient import Patient
from orm import omop, piano_api

class TestRondo(unittest.TestCase):

    def setUp(self):
        self.project_id = "test_rondo_integration"

    def tearDown(self):
        pass

    def test_connect_crucible(self):
        configs = piano_api.get_configs(self.project_id, "projectdata")
        assert len(configs) > 0
        config = configs[0]
        _id = config["_id"]
        config = piano_api.get_config(self.project_id, "projectdata", _id)
        assert config["_id"] == _id

    def test_connect_query(self):
        result = piano_api.query_config(self.project_id, "projectdata", _id=self.project_id)
        assert result[0]['_id'] == self.project_id

    def test_connect_query_in(self):
        result = piano_api.query_config(self.project_id, "projectdata", _id=[self.project_id])
        assert result[0]['_id'] == self.project_id

    def test_connect_query_in(self):
        result = piano_api.query_config(self.project_id, "projectdata", _id=[self.project_id])[0]
        result["test_val"] = test_val = uuid.uuid4().hex
        _id = piano_api.save_config(self.project_id, "projectdata", result)
        result = piano_api.query_config(self.project_id, "projectdata", _id=_id)
        assert result[0]['test_val'] == test_val

    def test_connect_omop(self):
        myOmop = omop.OMOP(self.project_id, 'Person', select="*", where="person_id=1", order_by="person_id", 
            limit=1, offset=0, as_list=False, reidentify=False)
        results = myOmop.execute()
        assert results[0]['person_id'] == 1

    def test_patient(self):
        patient = Patient.filter(self.project_id, person_id=1)[0]
        assert patient.person_id == '1'

    def test_patient_update(self):
        patient = Patient.filter(self.project_id, person_id=1)[0]
        patient.test_val = test_val = uuid.uuid4().hex
        patient.save()
        patient = Patient.filter(self.project_id, person_id=1, test_val=test_val)[0]
        assert patient.person_id == '1'    

    def test_patient_omop(self):
        patient = Patient.filter(self.project_id, person_id=1, omop='Person')[0]
        assert patient.person_id == '1'   
        assert patient._Person['person_id'] == 1    


if __name__ == '__main__':
    unittest.main()