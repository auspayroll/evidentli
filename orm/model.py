from . import piano_api as api
import sys


class Model(object):
	def __init__(self, project_id, *args, **kwargs):
		assert 'id' not in kwargs
		assert '_id' not in kwargs
		super(Model, self).__setattr__("_field_updates", {})
		#check for allowable fields are of the correct type
		if hasattr(self.__class__, "_fields"):
			_fields = self.__class__._fields
			assert type(_fields) in [list, dict]
			if type(_fields) is list:
				_fields = dict([(i, None) for i in _fields])
		else:
			_fields = {}

		for k, v in kwargs.items():
			if _fields:
				if k not in _fields.keys():
					raise AttributeError("%s is not in allowable fields %s" % (k, str(list(_fields.keys()))))
				_type = _fields.get(k)
				if _type:
					if _type is str:
						try:
							v = str(v)
						except:
							raise TypeError("%s should be of type %s" % (k, _type))
					elif type(v) is not _type:
						raise TypeError("%s should be of type %s" % (k, _type))

			setattr(self, k, v)
		super(Model, self).__setattr__("_project_id", project_id)

	def __getattr__(self, name):
		return None
	
	def __setattr__(self, name, value):
		if name[0] != '_':
			#the field value has changed, add it to _field_updates
			if hasattr(self, name) and getattr(self, name) != value or not hasattr(self,name):
				updates = self._field_updates
				updates[name] = value
				#prevent recursive calls to __setattr__
				super(Model, self).__setattr__("_field_updates", updates)
			elif value is None:
				pass

		super(Model, self).__setattr__(name, value)


	@property
	def _json(self):
		items = { "_id": self._id, "_project_id": self._project_id }
		for k,v in self.__dict__.items():
			if k[0] != '_':
				items[k] = v
		return items

	@classmethod
	def get(cls, project_id, id, json=False, *args, **kwargs):
		record = api.get_config(project_id, cls._name, id)
		record["_project_id"] = project_id
		if json:
			return record
		else: 
			return cls.create(**record)


	@classmethod
	def upsert(cls, project_id, defaults = {}, *args, **kwargs):
		if not kwargs:
			raise Exception("upsert error: no match keys specified")

		matches = cls.filter(_project_id, **kwargs)
		if not matches:
			fields = defaults.update(kwargs)
			model = cls(project_id=_project_id, **fields)
			model.save()
			return model
		elif len(matches) == 1:
			match = matches[0]
			match.update(**defaults)
			return match
		else:
			raise Exception("upsert error: More than 1 object matched")

			

	@classmethod
	def create(cls, _project_id, _id, *args, **kwargs):
		""" 
		used to create a model from a json dict with no pending 
		change updates, ie _field_updates
		"""
		model = cls(*args, project_id=_project_id)
		super(Model, model).__setattr__("_id", _id)
		for k, v in kwargs.items():
			setattr(model, k, v)
		model._field_updates.clear()
		return model

	@classmethod
	def filter(cls, project_id, json=False, *args, **query):
		results = api.query_config(project_id, cls._name, **query)
		if results is not None:
			items = []
			for result in results:
				result['_project_id'] = project_id
				if not json:
					item = cls.create(**result)
				else:
					item = result
				items.append(item)
			return items

	@classmethod
	def all(cls, project_id, json=False, *args, **kwargs):
		results = api.get_configs(project_id, cls._name)
		if results is not None:
			items = []
			for result in results:
				result['_project_id'] = project_id
				if not json:
					item = cls.create(**result)
				else:
					item = result
				items.append(item)
			return items

	def save(self):
		assert self._project_id
		if self._id:
			payload = { "_id": self._id}
			payload.update(self._field_updates)
		else:
			payload = self._field_updates
		valid = api.save_config(self._project_id, self.__class__._name, payload)
		if valid:
			self._id = valid
			self._field_updates.clear()
			return self._id
		else:
			return False


	def update(self, **kwargs):
		kwargs.pop("_id", None)
		kwargs.pop("id", None)
		assert self._id and self._project_id
		for k, v in kwargs.items():
			setattr(self, k, v)
		return self.save()


