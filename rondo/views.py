from rondo import app
from rondo_model import Rondo
from flask import jsonify as jsn
from flask import request
from functools import wraps
from orm import Patient, omop


def cors(f):
    @wraps(f)
    def adjust_headers(*args, **kwargs):
        if request.method == 'OPTIONS':
            response = jsn({'message': 'options'})
        else:
            response = f(*args, **kwargs)
        if app.config['CORS']:
            response.headers["Access-Control-Allow-Origin"] = '*'
            response.headers["Access-Control-Allow-Headers"] = "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, \
                Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers, Access-Control-Allow-Origin"

            response.headers["Access-Control-Allow-Methods"] = 'GET,HEAD,OPTIONS,POST,PUT'
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers['X-Application-Context'] = 'application'
        return response
    return adjust_headers



@app.route('/test', methods=['GET', 'OPTIONS'])
def test():
    return jsn({ 'message': 'Hello World!, welcome to Rondo test' })

@app.route('/', methods=['GET', 'OPTIONS'])
def index():
    return jsn({ 'message': 'Hello World!, welcome to Rondo' })


@app.route('/projects/<project_id>/rondo', methods=['GET', 'OPTIONS'])
@cors
def all(project_id):
    rondo = Rondo.all(project_id=project_id, json=True)
    return jsn(rondo)


@app.route('/projects/<project_id>/rondo', methods=['POST', 'OPTIONS'])
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


@app.route('/projects/<project_id>/rondo/<config_id>', methods=['GET', 'OPTIONS'])
@cors
def getRondo(project_id, config_id):
    rondo = Rondo.get(project_id=project_id, id=config_id, json=True)
    return jsn(rondo)


@app.route('/projects/<project_id>/rondo/<rondo_id>/flowfile', methods=['POST', 'OPTIONS'])
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
    if rondo.random:
        rondo.allocate_random_cohort(patient, force=True)
        if patient.cohort:
            json["cohort"] = patient.cohort
        if patient.pair_id:
            json["pair_id"] = patient.pair_id
    else:
        rondo.match_patient(patient)
        if patient.cohort:
            json['cohort'] = patient.cohort
    return jsn(json)


@app.route('/projects/<project_id>/schema', methods=['GET', 'OPTIONS'])
@cors
def getSchema(project_id):
    response = omop.get_schema(project_id)
    if 'tables' in response:
        return jsn({ "tables": response['tables']})
    else:
        return jsn(response)