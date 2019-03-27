from rondo import app
from rondo.models import Rondo
from flask import jsonify as jsn
from flask import request

@app.route('/')
def index():
    return 'Hello World!'

@app.route('/projects/<project_id>/rondo', methods=['POST'])
def createRondo(project_id):
	posted = request.get_json()
	rondo = Rondo(project_id=project_id, **posted)
	rondo.save()
	return jsn(rondo.config_id)

@app.route('/projects/<project_id>/rondo/<config_id>', methods=['GET'])
def getRondo(project_id, config_id):
	rondo = Rondo(project_id=project_id, config_id=config_id)
	rondo.load()
	return jsn(rondo.__dict__)

@app.route('/projects/<project_id>/rondo', methods=['GET'])
def getConfigs(project_id):
	configs = Rondo.get_all_configs(project_id)
	return jsn(configs)	

@app.route('/projects/<project_id>/patients', methods=['GET'])
def patients(project_id):
	rondo = Rondo(project_id=project_id, config_id='abc')
	patients = rondo.get_all_patients()
	return jsn(patients)

@app.route('/projects/<project_id>/patient/<patient_id>', methods=['GET'])
def patient(project_id, patient_id):
	rondo = Rondo(project_id=project_id, config_id='abc')
	patient = rondo.get_patient(patient_id)
	return jsn(patient)

@app.route('/project/<project_id>/flowfile', methods=['POST'])
def flowfile(project_id):
	patient = request.get_json()
	rondo = Rondo(project_id=project_id, config_id='abc')
	rondo.allocate_random_cohort(patient)
	rondo.match_patient(patient)
	return jsn(patient)


