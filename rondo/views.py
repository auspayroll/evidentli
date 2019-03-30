from rondo import app
from rondo.rondo import Rondo, Patient
from flask import jsonify as jsn
from flask import request

@app.route('/')
def index():
    return 'Hello World!, welcome to Rondo'

@app.route('/projects/<project_id>/rondo', methods=['POST'])
def createRondo(project_id):
	posted = request.get_json()
	rondo = Rondo(project_id=project_id, **posted)
	rondo.save()
	return jsn(rondo)

@app.route('/projects/<project_id>/rondo/<config_id>', methods=['GET'])
def getRondo(project_id, config_id):
	rondo = Rondo.get_config(project_id=project_id, id=config_id)
	return jsn(rondo.__dict__)

@app.route('/projects/<project_id>/rondo', methods=['GET'])
def getRondos(project_id):
	configs = Rondo.get_configs(project_id=project_id)
	return jsn(configs)	

@app.route('/projects/<project_id>/flowfile/<rondo_id>', methods=['POST'])
def flowfile(project_id, rondo_id):
	"""
	endpoint used for nifi processor. It accepts patient json, 
	and returns modified json as the flow file.
	"""
	json = request.get_json()	
	patient = Patient.create(**json)
	rondo = Rondo.get(project_id=project_id, id=rondo_id)
	rondo.allocate_random_cohort(patient)
	rondo.match_patient(patient)
	return jsn(patient._json)


