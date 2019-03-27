class Model(object):
	def __init__(self, *args, **kwargs):
		self._field_updates = {}
		for k, v in kwargs.items():
			setattr(self, k, v)

	def __getattr__(self, name):
		return None

	
	def __setattr__(self, name, value):
		if name[0] != '_':
			if hasattr(self, name) and getattr(self, name) != value or not hasattr(self,name):
				updates = self._field_updates
				updates[name] = value
				super().__setattr__("_field_updates", updates)
		super().__setattr__(name, value)