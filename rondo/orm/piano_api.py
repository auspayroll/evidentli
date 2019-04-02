import requests
from config import PIANO_API

PROJECTS_URL = PIANO_API + '/projects'


def save_config(project_id, config_name, payload):
    response = requests.post(PIANO_API + '/projects/%s/%s' % (project_id, config_name), json=[payload])
    if response.status_code == requests.codes.ok:
        jsn = response.json()
        if type(jsn) is list:
            return jsn[0]
        else:
            return jsn


def get_config(project_id, config_name, config_id):
    response = requests.get(PROJECTS_URL + '/%s/%s/%s' % (project_id, config_name, config_id))
    if response.status_code == requests.codes.ok:
        jsn = response.json()
        if type(jsn) is list:
            return jsn[0]
        else:
            return jsn


def get_configs(project_id, config_name):
    response = requests.get(PROJECTS_URL + '/%s/%s' % (project_id, config_name))
    if response.status_code == requests.codes.ok:
        jsn = response.json()
        return jsn


def query_config(project_id, config_name, query):
    querystring = ";".join([ "%s='%s'" % (k,v) for (k,v) in query.items()])
    """
    terms = []
    for (k,v) in query.items():
        if type(v) is str:
            terms[k] = str(k) + "='" + v + "'"
        else:
            terms[k] = str(k) + "=" + str(v)

    querystring = ";".join(terms)
    """
    request_string = PROJECTS_URL + "/%s/%s?query=AND(%s)" % (project_id, config_name, querystring)
    response = requests.get(request_string)
    if response.status_code == 200 and response.content:
        return response.json()
