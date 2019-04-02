from rondo import app
from rondo.rondo_model import Rondo, Patient
from flask import jsonify as jsn
from flask import request


@app.route('/')
def index():
    return 'Hello World!, welcome to Rondo'


@app.route('/projects/<project_id>/rondo', methods=['GET'])
def all(project_id):
    rondo = Rondo.all(project_id=project_id, json=True)
    return jsn(rondo)


@app.route('/projects/<project_id>/rondo', methods=['POST'])
def createRondo(project_id):
    posted = request.get_json()
    _id = posted.get("_id")
    if _id:
        rondo = Rondo.get(project_id=project_id, id=_id)
        rondo.update(**posted)
    else:
        rondo = Rondo(project_id=project_id, **posted)
        rondo.save()
    return jsn(rondo._json)


@app.route('/projects/<project_id>/rondo/<config_id>', methods=['GET'])
def getRondo(project_id, config_id):
    rondo = Rondo.get(project_id=project_id, id=config_id, json=True)
    return jsn(rondo)


@app.route('/projects/<project_id>/rondo/<rondo_id>/flowfile', methods=['POST'])
def flowfile(project_id, rondo_id):
    """
    endpoint used for nifi processor. It accepts patient json,
    and returns modified json as the flow file.
    """
    json = request.get_json()
    patient = Patient.create(_project_id=project_id, **json)
    rondo = Rondo.get(project_id=project_id, id=rondo_id)
    rondo.allocate_random_cohort(patient)
    rondo.match_patient(patient)
    if patient.pair_id:
        json["pair_id"] = patient.pair_id
    if patient.cohort:
        json['cohort'] = patient.cohort
    return jsn(json)
