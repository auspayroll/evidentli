import hashlib
import uuid
import requests
import urllib

PROJECT_ID = 'test_michael2'
PIANO_API = 'http://dev.api.evidentli.com'
cohorts = ['Cohort A', 'Cohort B', 'Cohort C']
test_patient_id = "5c906949847f3f001b747a00"
get_patients = PIANO_API + '/projects/' + PROJECT_ID + '/patients'


def store_in_patient(id, key, value):
    r = requests.post(PIANO_API + "/projects/%s/patients" % PROJECT_ID,
                   json=[{"_id": str(id), key: str(value)}])
    if r.status_code == requests.codes.ok and r.content:
        return True
    return False


def query_project_patients(query):
    querystring = ";".join([ "%s='%s'" % (k,v) for (k,v) in query.items()])
    request_string = get_patients + "?query=AND(%s)" % querystring
    print(request_string)
    response = requests.get(request_string)
    if response.status_code == 200 and response.content:
        return response.json()
    else: 
        []

def match_patient(pair_id, criteria):
    patient_matches = query_project_patients(find_match)
    for patient_match in patient_matches:
        if not patient_match.get("pair_id"): # only select unmatched patients
            patient_id = patient_match.get("person_id")
            if patient_id is not None:
                 store_in_patient(patient_id, "pair_id", pair_id) 

def main(flowfile):
    # get cohorts from configuration
    person_id = flowfile.get("person_id")
    if person_id is None:
        return None
    no_cohorts = len(cohorts)  
    cohort_no = int(hashlib.sha256(str(person_id).encode("utf-8")).hexdigest(), 16) % no_cohorts
    allocated_cohort = cohorts[cohort_no]
    store_in_patient(person_id, "cohort", allocated_cohort)
    flowfile['cohort'] = allocated_cohort

    """
    patient_cohort = allocated_cohort
    #matched pairs
    flowfile['pair_id'] = pair_id =  flowfile.get("pair_id")
    if pair_id is None:
        pair_id = uuid.uuid4().hex
        find_match = {}
        for field_match in matched_pairs:
            field_match_value = flowfile.get(field_match)
            if field_match_value is None: #patient has no field
                continue
            find_match[field_match] = field_match_value
            if cohorts: #find matching pair for each cohort
                for cohort in cohorts:
                    if cohort == patient_cohort:
                        continue # query other cohorts
                    find_match["cohort"] = cohort
                    match_patient(pair_id, find_match)
            else: #find a matching pair amongst all patients
                match_patient(pair_id, find_match)
    """

                                                                       