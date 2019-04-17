from .model import Model
from .patient import Patient


class Project(object):
	def __init__(self, project_id, *args, **kwargs):
		self._id = project_id
		self._patients = []

	def get_patients(self, **query):
		if query:
			self._patients = Patient(project_id=self._id).filter(**query)
		else:
			self._patients = Patient(project_id=self._id).all()
		return self._patients

	@property
	def patients(self):
		return self._patients

	def get_patient(self, id):
		return Patient.get(project_id=self._id, id=id)


class ProjectData(Model):
	_name = "projectdata"

	def __repr__(self):
		if hasattr(self, "project_title") and hasattr(self, "_id"):
			return "<ProjectData title: %s>" % self.project_title
		elif hasattr(self, "_id"):
			return "<ProjectData id: %s>" % self._id
		else:
			return "<ProjectData: not loaded>"
