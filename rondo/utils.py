from flask.json import JSONEncoder


class ModelJsonEncoder(JSONEncoder):
	def default(self, o):
		items = { "_id": o._id, "_project_id": o._project_id }
		for k,v in o.__dict__.items():
			if k[0] != '_':
				items[k] = str(v)
		return items