from .model import Model
from . import omop
import dateutil.parser as parser


class Patient(Model):
	_name = "patients"
	_omop_name = 'person'

	def __repr__(self):
		if hasattr(self, "_id"):
			return "<Patient id: %s>" % self._id
		else:
			return "<Patient: not loaded>"

	def fieldValue(self, field_expression):
		multiField = False
		field = field_expression
		field_parts = field.split(' ')
		len_field_parts = len(field_parts)
		if len_field_parts > 2:
			multiField = True
		if len_field_parts == 1:
			table, fieldname = field.split('.')
			table = table.title()
			fieldname = fieldname.lower()
		if len_field_parts == 2:
			table, fieldname = field_parts[0].split('.')
			table = table.title()
			fieldname = fieldname.lower()
			field_label = field_parts[1]
		elif len_field_parts > 2:
			table1, fieldname1 = field_parts[0].split('.')
			table2, fieldname2 = field_parts[2].split('.')
			table1 = table1.title()
			table2 = table2.title()
			fieldname1 = fieldname1.lower()
			fieldname2 = fieldname2.lower()

		if multiField:
			try:
				value1 = float(getattr(self, "_%s" % (table1)).get(fieldname1)) 
				value2 = float(getattr(self, "_%s" % (table2)).get(fieldname2)) 
				return utils.operate(value1, symbol, value2)
			except:
				try: # try to parse as date
					value1 = parser.parse(getattr(self, "_%s" % (table1)).get(fieldname1))
					value2 = parser.parse(getattr(self, "_%s" % (table1)).get(fieldname1))
					return float((value1 - value2).days)
				except:
					return None	
		else:
			try:
				return float(getattr(self, "_%s" % (table)).get(fieldname))   
			except: # to do , try parse as date
				try:
					return getattr(self, "_%s" % (table)).get(fieldname)
				except:
					return None



	@classmethod
	def filter(cls, project_id, *args, **kwargs):
		omop_tables = kwargs.pop('omop', None)
		results = super(Patient, cls).filter(*args, project_id=project_id, **kwargs)
		if not results:
			return []
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
					table_field = "_%s" % table.title()
					super(Model, patient).__setattr__(table_field, {})
					omop_patient_values = patient_dict.get(int(patient.person_id))
					if omop_patient_values:	
						super(Model, patient).__setattr__(table_field, omop_patient_values)
		return results					
					