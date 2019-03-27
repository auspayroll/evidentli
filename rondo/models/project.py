from .model import Model

class Project(Model):
	def __repr__(self):
		if hasattr(self, "project_title") and hasattr(self, "_id"):
			return "<Project title: %s>" % self.project_title
		elif hasattr(self, "_id"):
			return "<Project id: %s>" % self._id
		else:
			return "<Project: not loaded>"

	def fetch(self):
		if self._id:
			project_data = api.get_project_data(self._id)
			for k, v in project_data.items():
				setattr(self, k, v)
			self._field_updates.clear()

		else:
			raise Exception("Project id not set")

	def save(self):
		payload = { _id: self._id, **self._field_updates }
		api.save_project(self._id, payload)

	@property
	def patients(self):
		if hasattr(self, '_patients'):
			return self._patients
		else:
			[]

	def get_patients(self):
		self._patients = [Patient(**rec) for rec in api.get_patients(self._id)]
		for patient in self._patients:
			patient.project_id = self._id
		return self._patients