import requests
import rondo
import library


cohorts = ['Cohort A', 'Cohort B', 'Cohort C']
test_patient_id = "5c906949847f3f001b747a00"
test_patient_id2 = '5c90694a847f3f001b747a01'


if __name__ == "__main__":
	project_id = 'test_michael2'
	cohorts = ['M', 'N', 'P']
	matched_pairs = ['age']
	myRondo = rondo.Rondo(project_id=project_id, cohorts=cohorts, 
		config_id='abc', matched_pairs=matched_pairs)
	
	patient = myRondo.get_patient(test_patient_id)
	#patients = myRondo.get_all_patients()
	result = myRondo.match_patient(patient)
	print(result)
	
	#library.store_in_patient(project_id, test_patient_id2, "age", 20)



	
