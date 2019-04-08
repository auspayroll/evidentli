from rondo import app
from rondo.rondo_model import Rondo, Patient
from flask import jsonify as jsn
from flask import request
from functools import wraps



def cors(f):
    @wraps(f)
    def adjust_headers(*args, **kwargs):
        response = f(*args, **kwargs)
        if app.config['CORS']:
            response.headers["Access-Control-Allow-Origin"] = '*'
            response.headers["Access-Control-Allow-Headers"] = "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, \
                Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers"

            response.headers["Access-Control-Allow-Methods"] = 'GET,HEAD,OPTIONS,POST,PUT'
            response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    return adjust_headers


@app.route('/')
def index():
    return 'Hello World!, welcome to Rondo'


@app.route('/projects/<project_id>/rondo', methods=['GET'])
@cors
def all(project_id):
    rondo = Rondo.all(project_id=project_id, json=True)
    return jsn(rondo)


@app.route('/projects/<project_id>/rondo', methods=['POST'])
@cors
def createRondo(project_id):
    json = request.get_json()
    json.pop('project_id', None)
    json.pop('_project_id', None)
    _id = json.get("_id")
    if _id:
        rondo = Rondo.get(project_id=project_id, id=_id)
        rondo.update(**json)
    else:
        rondo = Rondo(project_id=project_id, **json)
        rondo.save()
    return jsn(rondo._json)


@app.route('/projects/<project_id>/rondo/<config_id>', methods=['GET'])
@cors
def getRondo(project_id, config_id):
    rondo = Rondo.get(project_id=project_id, id=config_id, json=True)
    return jsn(rondo)


@app.route('/projects/<project_id>/rondo/<rondo_id>/flowfile', methods=['POST'])
@cors
def flowfile(project_id, rondo_id):
    """
    endpoint used for nifi processor. It accepts patient json,
    and returns modified json as the flow file.
    """
    json = request.get_json()
    json.pop('project_id', None)
    json.pop('_project_id', None)
    patient = Patient.create(_project_id=project_id, **json)
    rondo = Rondo.get(project_id=project_id, id=rondo_id)
    rondo.allocate_random_cohort(patient)
    rondo.match_patient(patient)
    if patient.pair_id:
        json["pair_id"] = patient.pair_id
    if patient.cohort:
        json['cohort'] = patient.cohort
    return jsn(json)
