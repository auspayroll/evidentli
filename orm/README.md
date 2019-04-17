# ORM 

The ORM is a Python client API wrapper to connect to the PIANO API. It makes writing code more convenient and intuitive by working with Python objects rather than lower level JSON dictionaries and HTTP requests. 

Currently this package currently resides in the [RONDO](../../README.md) repository, but should ideally should have its own. 

---

## Model classes

A model class represents a configuration collection belonging to Piano projects.

The following model classes are currently defined:

- ProjectData
- Patient
- Reference

Access from the Python terminal

``> from orm.model import ProjectData  ``

See what methods are avaialble as normal

``> dir(ProjectData)``

---

## Creating model classes

 Defining a new  model class is easy. By subclassing the ``Model`` class, derived objects have access to ORM functionality descibed below. 

```
from orm.model import Model

class Reference(Model):
    _name = "references"
    _fields = { 'rego': str, authors: list, 'items': dict } #optional

```

The bare minimum to create model class, is a ``_name`` attribute, which is the label/id of the backend MongoDB collection for a project.

### _fields

To allow only a certain set of fields, specify a dictionary attribute ``_fields`` with field name as key and a python type as value. Optionally just specify a python list with field names. Any attributes other than those specified will result in an ``AttributeError``. If types are specified, incorrect types will throw a ``TypeError``. The ``_fields`` attribute is not mandatory. 

### Underscore _attributes
Model objects who attributes begin with an underscore are **not** saved to the backend datastore. These are used for convenience on the client side only. Model objects have ``_id`` and ``_project_id`` attributes automatically set and should not be changed. 

---

## Creating new records

``> config = MyConfig(name="My Config") ``

``> config.save()``

Model objects are created in the same manner as normal Python objects, however are only saved to the PIANO backend when the ``save`` method is called.

---

## Fetching records

Use the model class method ``get`` to retrieve single records as model objects. Both ``project_id`` and ``id`` parameters are required.

``> patient = Patient.get(project_id='my_project', id="patient_id")``

The ``all`` class method returns a list of model objects which can be iterated on as normal.

``> patients = Patient.all(project_id='my_project') ``

``> for patient in patients: print(patient.person_id)``


---

## Querying records

Models can be queried using the class method ``filter`` which receive keyword arguments as search criteria. Model objects are searched by logically ANDing keyword arguments. 

``> patients = Patient.filter(lastname="Smithers", age="29") ``

In this example, a list of patients whose lastname is `Smithers` __and__ age is `29`. Currently there is only provision to support string values, and logical OR operations are not supported. This may change in the future. 

### ToDo
* Logical OR operations
* `limit` keyword to limit the number of fetched records
* support for queries on numeric fields
* support for comparitive search (less than, greater than) on numeric fields



---

## Updating records

``> patient.firstname = "Donald" ``

``> patient.save() ``

  For efficiency, only changes to model object attributes are sent to the PIANO API for updating. Changes are only send when an objects ``save()`` method is called. Pending changes are stored in the  ``_field_updates`` attribute and generally shouldn't be changed. 

  To update many fields at a time for an object, use the ``update`` method, that takes keyword arguments for each field. 

  ``> updates = { "firstname" = "Kim", middlename="Jong", lastname="Un"}``

  ``> patient.update(**updates)``

---

## Creating model objects from a dictionary

It some scenarios, it may be required to create a model object from a Python dictionary, for example, a json object may be recieved from HTTP POST request that represents a patient record. 

In these cases, a Model class's ``create`` function can be used to create a model from a dictionary without having to query the PIANO API. ``create`` takes keywork arguments as object attributes. To pass in a dictionary, use Python's spread operator   ``**``.



``> patient_dict = { _id: '343', _project_id: 'my_project', firstname: 'Henry' }``

``> my_patient = Patient.create(**patient_dict)``

When using ``create``, the fields ``_id`` and ``_project_id`` are required. 

---

## The Project class
The Project class is not a model class as it does not represent a database collection or record. It simply provides convenience methods which make use of model class methods. 

Instantiate a Project class with an existing project key

``> my_project = Project("my_project_key")``


A project object saves having to provide a project key for each query. For example, to get project patients, instead of having to write

``> patients = Patient.all(project_id)``

Create a project object and use one of the supported convenience methods, or write your own

``> all_patients = my_project.get_patients()``

``> b_cohort = my_project.get_patients(cohort="B")``

To return cached patients from previous call to the PIANO API through ``get_patients`` use the ``patients`` attribute

``> my_project.patients``

Subsequent calls to ``get_patients`` will update the cached patients on the project object. 













