import requests

PROJECT_ID = 'test_michael2'
PIANO_API = 'api.evidentli.com'
cohorts = ['Cohort A', 'Cohort B', 'Cohort C']

get_patients = PIANO_API + '/projects/' + PROJECT_ID + '/patients'

print("getting patients %s" % get_patients)

patients = requests.get(get_patients)

print(patients)