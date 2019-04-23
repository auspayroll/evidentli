from flask.json import JSONEncoder


class ModelJsonEncoder(JSONEncoder):
    def default(self, o):
        items = {"_id": o._id, "_project_id": o._project_id}
        for k, v in o.__dict__.items():
            if k[0] != '_':
                items[k] = str(v)
        return items

def sanitize_key(key):
	""" 
	sanitizes for storage in mongodb 
	"""
	key = key.strip()
	sanitized = []
	for i, char in enumerate(key):
		if char != ' ' and char < '0' or char > 'z' or char == "\\":
			sanitized.append('_')
		else:
			sanitized.append(char)
	return ''.join(sanitized)


def _split_string(value, sanitize=True):
	if not value:
		return []
	split_on = ','
	if split_on not in value:
		split_on = ' '
	if sanitize:
		keywords = [sanitize_key(x) for x in value.split(split_on)]
	else: 
		keywords = [x for x in value.split(split_on)]
	value_list = list(dict.fromkeys(keywords))
	return value_list


def categorize_by_list(categories, val):
	if not val or not categories:
		return categories
	if type(categories) is str:
		categories = _split_string(categories, sanitize=False)
	categories = [ float(c) for c in categories ]
	categories.sort()
	lt = [i for i in categories if i >= val]

	if not lt:
		cat  = '> %s' % categories[-1]
	elif len(lt) == len(categories):
		cat = '< %s' % categories[0]
	else:
		cat = '<= %s' % (lt[0] )
	return cat




