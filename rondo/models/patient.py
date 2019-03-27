from .model import Model

class Patient(Model):
	def __repr__(self):
		if hasattr(self, "_id"):
			return "<Patient id: %s>" % self._id
		else:
			return "<Patient: not loaded>"

		def fetch(self):
			if self._id and self.project_id:
				patient_data = api.get_patient(project_id, _id)
				self.__init__(**patient_data)
			else:
				raise Exception("patient id/project id not set")

		def save(self):
			payload = { _id: self._id, **self._field_updates }
			api.save_patient(self._id, payload)