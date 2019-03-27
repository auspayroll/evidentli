import requests

PROJECT_ID = 'test_michael2'
PIANO_API = 'http://dev.api.evidentli.com'
PROJECTS_URL = PIANO_API + '/projects'



def save_config(project_id, config_name, payload):
    response = requests.post(PIANO_API + '/projects/%s/%s' % (project_id, config_name), json=[payload])
    if response.status_code == requests.codes.ok:
        jsn = response.json()
        if type(jsn) is list:
            return jsn[0]
        else:
            return jsn

def save_project(project_id, payload):
    return save_config(project_id, "projectdata", payload)

def save_patient(project_id, payload):
    return save_config(project_id, "patients", payload)

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

def get_project_data(project_id):
    jsn = get_configs(project_id, 'projectdata')
    if type(jsn) is list:
        return jsn[0]
    else:
        return jsn

def get_patient(project_id, patient_id):
    return get_config(project_id, 'patients', patient_id)

def get_all_patients(project_id):
    return get_configs(project_id, "patients")


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
    else: 
        []

def query_patients(project_id, query):
    return query_config(project_id, "patients", query)

def get_patients(project_id, query=None):
    if query:
        return query_patients(project_id, query)
    else:
        return get_all_patients(project_id)


def match_patient(project_id, pair_id, criteria):
    patient_matches = query_patients(project_id, criteria)
    for patient_match in patient_matches:
        if not patient_match.get("pair_id"): # only select unmatched patients
            patient_id = patient_match.get("_id")
            if patient_id is not None:
                 store_in_patient(project_id, patient_id, "pair_id", pair_id) 
                 return True
    return False