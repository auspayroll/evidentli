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
		print(patient_ids)
		#import pdb
		#pdb.set_trace()
		if type(omop_tables) is str:
			omop_tables = omop_tables.split(',')
		elif type(omop_tables) is not list:
			return results
		for table in omop_tables:
			try:
				omop_patients = omop.get_omop(project_id=project_id, table='person', all_in=patient_ids)
			except:
				pass
			else:
				patient_dict = {}
				for op in omop_patients:
					patient_dict[op['person_id']] = op

				for patient in results:
					table_field = "_%s" % table.title()
					setattr(patient, table_field, {})
					table_dict = getattr(patient, table_field)
					setattr(patient, table_field, patient_dict[int(patient.person_id)])
					return results					
					