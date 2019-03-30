# RONDO 

Rondo is an application designed to work with the PIANO API. It works like any other PIANO application (such as PICCOLO etc) by making HTTP REST calls to the remote PIANO API. 

Rondo is written is a standalone Python package so it should be able to be included in any deployment scenario supporting Python. There are connecting REST endpoints available as a Python Flask application by default, but this is easily customizable. 

Rondo has two main features

1. To allocate random cohorts to patient files
2. To pair match patients on their attributes

---

## Usage
Rondo makes use of a simple ORM package (similar to Python Django) to make the code a little cleaner. Details can be found in the ORM package [README](rondo/orm/README.md) file. It's probably better to read that first. 

Once this package is installed, from the python command line, import the Rondo model. 

``> from rondo import Rondo``

Usage examples can be found in the package [test.py](rondo/test/test.py) file

---

## Random Cohorts
Rondo objects are created with a ``project_id``. Cohorts are given as a list of strings.

``> myRondo = Rondo(project_id="project_id", cohorts=["A", "B","C"]) ``

To allocate a random cohort, pass in a patient object to 

``> myRondo.allocate_random_cohort(patient)``

This will allocate a random cohort to the cohort field. The cohort is saved in the backend datastore.

``> patient.cohort ``

To manually set a cohort to a patient, just set as an attirubute to the patient object and save

``> patient.cohort = 'B'``

``> patient.save()``

---

## Matched Pairs

To create matched pairs, create a Rondo object by specifying a list of fields to match patients on

``> myRondo = Rondo(project_id="project_id", matched_pairs=["age", "gender"])``

To match a patient, pass in a patient object. This will return a list of matched patients. By default, there will be a single patient match to complete the pair. In this example, both patients will have the same age and gender.

``> matched_patients = myRondo.match_patient(patient)``

``> matched_patient = matched_patients[0]``

Both matched patients will have the same ``pair_id``, a randomly generated unique identifier.

``> matched_patient.pair_id == patient.pair_id ``

### Match Pairs by Cohort

By default, matched pairs will not take cohorts into account, ie matches will be based on all the patients as a whole. To carrying out matching based on cohorts, use the ``match_by_cohorts`` parameter, setting it to ``True``. 

``> myRondo = Rondo(project_id="project_id", matched_pairs=["age", "gender"], cohorts=["A", "B", "C"], match_by_cohort=True)``

``> matched_patients = myRondo.match_patient(patient)``

In this example, patients with the same age and gender from each of the cohorts will be assigned the same ``pair_id``. 

``> patient.pair_id == matched_patients[0].pair_id == matched_patient[1].pair_id``






