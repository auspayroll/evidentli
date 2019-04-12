from .model import Model
from . import omop


class Patient(Model):
	_name = "patients"

	def __repr__(self):
		if hasattr(self, "_id"):
			return "<Patient id: %s>" % self._id
		else:
			return "<Patient: not loaded>"


	@classmethod
	def filter(cls, project_id, *args, **kwargs):
		omop_tables = kwargs.pop('omop', None)
		results = super(Patient, cls).filter(*args, project_id=project_id, **kwargs)
		patient_ids = [ p.person_id for p in results ]
		if type(omop_tables) is str:
			omop_tables = [ t.strip() for t in omop_tables.split(',')]
		elif type(omop_tables) is not list:
			return results
		for table in omop_tables:
			try:
				omop_patients = omop.get_omop(project_id=project_id, table=table, all_in=patient_ids)
			except:
				pass
			else:
				patient_dict = {}
				for op in omop_patients:
					patient_dict[op['person_id']] = op

				for patient in results:
					table_field = "_%s" % table
					super(Model, patient).__setattr__(table_field, {})
					omop_patient_values = patient_dict.get(int(patient.person_id))
					if omop_patient_values:	
						super(Model, patient).__setattr__(table_field, omop_patient_values)
		return results					
					