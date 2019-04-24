from sumo import app
from .sumo_model import Sumo
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



@app.route('/', methods=['GET', 'OPTIONS'])
@cors
def index():
    return jsn({ 'message': 'Hello World!, welcome to Sumo!!' })


@app.route('/projects/<project_id>/sumo', methods=['GET', 'OPTIONS'])
@cors
def all(project_id):
    sumo = Sumo.all(project_id=project_id, json=True)
    return jsn(sumo)


@app.route('/projects/<project_id>/sumo', methods=['POST', 'OPTIONS'])
@cors
def createSumo(project_id):
    json = request.get_json()
    json.pop('project_id', None)
    json.pop('_project_id', None)
    _id = json.get("_id")
    if _id:
        sumo = Sumo.get(project_id=project_id, id=_id)
        sumo.update(**json)
    else:
        sumo = Sumo(project_id=project_id, **json)
        sumo.save()
    sumo.analyse()
    return jsn(sumo._json)


@app.route('/projects/<project_id>/sumo/<config_id>', methods=['GET', 'OPTIONS'])
@cors
def getSumo(project_id, config_id):
    sumo = Sumo.get(project_id=project_id, id=config_id, json=True)
    return jsn(sumo)


@app.route('/projects/<project_id>/sumo/<sumo_id>/stats', methods=['GET', 'OPTIONS'])
@cors
def stats(project_id, sumo_id):
    """
    endpoint used for nifi processor. It accepts patient json,
    and returns modified json as the flow file.
    """
    sumo = Sumo.get(project_id=project_id, id=sumo_id)
    return jsn(sumo.stats_by_field)


@app.route('/projects/<project_id>/sumo/<sumo_id>/calc_stats', methods=['GET', 'OPTIONS'])
@cors
def calc_stats(project_id, sumo_id):
    """
    endpoint used for nifi processor. It accepts patient json,
    and returns modified json as the flow file.
    """
    sumo = Sumo.get(project_id=project_id, id=sumo_id)
    sumo.analyse()
    return jsn(sumo.stats_by_field)

@app.route('/projects/<project_id>/schema', methods=['GET', 'OPTIONS'])
@cors
def getSchema(project_id):
    response = omop.get_schema(project_id)
    if 'tables' in response:
        return jsn({ "tables": response['tables']})
    else:
        return jsn(response)

