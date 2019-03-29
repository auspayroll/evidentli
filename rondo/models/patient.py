from .model import Model


class Patient(Model):
	_name = "patients"

	def __repr__(self):
		if hasattr(self, "_id"):
			return "<Patient id: %s>" % self._id
		else:
			return "<Patient: not loaded>"


