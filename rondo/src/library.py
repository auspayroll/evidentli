import requests

PROJECT_ID = 'test_michael2'
PIANO_API = 'http://dev.api.evidentli.com'

get_patients = PIANO_API + '/projects/%s/patients'

def store_in_patient(project_id, patient_id, key, value):
    r = requests.post(get_patients % project_id,
                   json=[{"_id": str(patient_id), key: str(value)}])
    if r.status_code == requests.codes.ok and r.content:
        return True
    return False

def get_patient(project_id, patient_id):
    query = get_patients + '/' + patient_id
    response = requests.get(query % project_id)
    return response.json()

def get_all_patients(project_id):
    response = requests.get(get_patients % project_id)
    if response.status_code == requests.codes.ok:
        return response.json()


def query_project_patients(project_id, query):
    querystring = ";".join([ "%s='%s'" % (k,v) for (k,v) in query.items()])
    request_string = (get_patients + "?query=AND(%s)") % (project_id, querystring)
    response = requests.get(request_string)
    if response.status_code == 200 and response.content:
        return response.json()
    else: 
        []

def match_patient(project_id, pair_id, criteria):
    patient_matches = query_project_patients(project_id, criteria)
    for patient_match in patient_matches:
        if not patient_match.get("pair_id"): # only select unmatched patients
            patient_id = patient_match.get("_id")
            if patient_id is not None:
                 store_in_patient(project_id, patient_id, "pair_id", pair_id) 
                 return True
    return False