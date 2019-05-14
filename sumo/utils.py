from flask.json import JSONEncoder
import operator


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
	sanitized = []
	for i, char in enumerate(key):
		if char == '.':
			sanitized.append('__')
		elif char != ' ' and char < '0' or char > 'z' or char == "\\":
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
		keywords = [sanitize_key(x.strip()) for x in value.split(split_on)]
	else: 
		keywords = [x.strip() for x in value.split(split_on)]
	#value_list = list(dict.fromkeys(keywords))
	return keywords


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

def operate(operand1, symbol, operand2):
	default = 0
	if symbol == '-':
		try:
			return operand1 - operand2
		except:
			return default
	if symbol == '+':
		try:
			return operand1 - operand
		except:
			return default
	if symbol == '/':
		try:
			return float(operand1) / float(operand2)
		except:
			return default
	elif symbol == '*':
		try:
			return float(operand1) * float(operand2)
		except:
			return default
	elif symbol == '>':
		try:
			return int(operand1 > operand2)
		except:
			return default
	elif symbol == '>=':
		try:
			return int(operand1 >= operand2)
		except:
			return default
	elif symbol == '<':
		try:
			return int(operand1 < operand2)
		except:
			return default
	elif symbol == '<=':
		try:
			return int(operand1 <= operand2)
		except:
			return default


def getfieldparts(field_expression):
	field_parts = [ x.strip() for x in field_expression.split(' ')]
	yields = []
	if len(field_parts) in (1,2):
		try:
			table, fieldname = field_parts[0].split('.')          
		except:
			pass
		else:
			yielded = True
			yields.append((sanitize_key(table.capitalize()), fieldname.lower()))

	elif len(field_parts) >= 3:
		try:
			table, fieldname = field_parts[0].split('.')          
		except:
			pass
		else:
			yielded = True
			yields.append((sanitize_key(table.capitalize()), fieldname.lower()))

		try:
			table, fieldname = field_parts[2].split('.')          
		except:
			pass
		else:
			yielded = True
			yields.append((sanitize_key(table.capitalize()), fieldname.lower()))
	
	for y in yields:
		yield y




