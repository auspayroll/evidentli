from rondo import piano_api as api

class Model(object):
	def __init__(self, *args, **kwargs):
		assert 'project_id' in kwargs
		assert 'id' not in kwargs
		assert '_id' not in kwargs
		_project_id = kwargs.pop('project_id')
		setattr(self, '_project_id', _project_id)
		self._field_updates = {}

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
					if type(v) is not _type:
						raise TypeError("%s should be of type %s" % (k, _type))

			setattr(self, k, v)

	def __getattr__(self, name):
		return None
	
	def __setattr__(self, name, value):
		if name[0] != '_':
			#the field value has changed, add it to _field_updates
			if hasattr(self, name) and getattr(self, name) != value or not hasattr(self,name):
				updates = self._field_updates
				updates[name] = value
				#prevent recursive calls to __setattr__
				super().__setattr__("_field_updates", updates)
			elif value is None:
				pass
		super().__setattr__(name, value)

	@property
	def _json(self):
		items = { "_id": self._id, "_project_id": self._project_id }
		for k,v in self.__dict__.items():
			if k[0] != '_':
				items[k] = str(v)
		return items

	@classmethod
	def get(cls, *args, **kwargs):
		_id = kwargs.get("id")
		_project_id = kwargs.get("_project_id", kwargs.get("project_id"))
		assert _id and _project_id
		json = api.get_config(_project_id, cls._name, _id)
		json["_project_id"] = _project_id
		return cls.create(**json)

	@classmethod
	def create(cls, *args, **kwargs):
		""" 
		used to create a model from a json dict with no pending 
		change updates, ie _field_updates
		"""
		assert "_project_id" in kwargs and "_id" in kwargs
		_id = kwargs.pop('_id')
		_project_id = kwargs.pop('_project_id')
		model = cls(*args, **kwargs, project_id=_project_id)
		model._id = _id
		model._field_updates.clear()
		return model

	@classmethod
	def filter(cls, *args, **query):
		assert 'project_id' in query
		project_id = query.pop('project_id')
		results = api.query_config(project_id, cls._name, query)
		if results is not None:
			items = []
			for result in results:
				result['_project_id'] = project_id
				item = cls.create(**result)
				items.append(item)
			return items

	@classmethod
	def all(cls, project_id, *args, **kwargs):
		results = api.get_configs(project_id, cls._name)
		if results is not None:
			items = []
			for result in results:
				result['_project_id'] = project_id
				item = cls.create(**result)
				items.append(item)
			return items

	def save(self):
		assert self._project_id
		if self._id:
			payload = { "_id": self._id, **self._field_updates }
		else:
			payload = self._field_updates
		valid = api.save_config(self._project_id, self.__class__._name, payload)
		if valid:
			self._id = valid
			self._field_updates.clear()
			return self._id

		

