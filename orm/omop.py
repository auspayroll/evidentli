import requests
import json
from functools import reduce
from config import Config
import string_utils

success_codes = [requests.codes.ok]

def raw_sql(project_id, sql, verb='POST', as_list=False, reidentify=False):
	payload = { "query": sql, "reidentify": reidentify }
	if as_list:
		payload["format"] = "list"

	headers = { 'AUTHKEY': Config.EOBO_KEY, 'Content-Type': 'application/json'}
	request_url = Config.PIANO_API + '/projects/' + project_id + '/omop'
	if verb == 'POST':
		response = requests.post(request_url, json=payload, headers=headers)
	else:
		response = requests.get(request_url, json=payload, headers=headers)
	
	if response.status_code in success_codes:
		rows = response.json()
		return rows['rows']
	else:
		raise Exception("Remote query failed url: %s, EOBO authkey: %s" % (request_url, Config.EOBO_KEY))

class OMOP(object):
	def __init__(self, project_id, table, select=None, where=None, order_by=None, 
			limit=None, offset=None, as_list=False, reidentify=False, all_in=[], *args, **kwargs):
		self.as_list = as_list
		self.reidentify = reidentify
		self._project_id = project_id
		table = string_utils.camel_case_to_snake(table)
		if type(select) is str:
			query = "select %s from %s " % (select, table)
		elif type(select) is list:
			query = "select %s from %s " % (', '.join(select), table)
		else:
			query = "select * from %s " % table

		if where: 
			if type(where) is dict:
				where_clauses = []
				for k, v in where.items():
					if type(v) is str:
						where_clauses.append("%s = '%s'" % (k, v))
					else:
						where_clauses.append("%s = %s" % (k, v))
				query = query + "where " + " and ".join(where_clauses)
			else:
				query = query + "where %s " % where

		if where and all_in:
			query = query + "and person_id in " + str(all_in).replace('[','(').replace(']',')')
		elif all_in:
			query = query + "where person_id in " + str(all_in).replace('[','(').replace(']',')')

		if order_by:
			query = query + " order by %s " % order_by

		if limit and type(limit) in (str, int):
			query = query + " limit %s " % limit

		if offset and type(offset) in (str, int):
			query = query + " offset %s " % offset
		self.query = query

	def execute(self):
		response = raw_sql(self._project_id, self.query, 'POST', self.as_list, self.reidentify)
		return response


def get_omop(*args, **kwargs):
	obj = OMOP(*args, **kwargs)
	return obj.execute()


def get_omop_old(project_id, table, select=None, where=None, order_by=None, 
	limit=None, offset=None, as_list=False, reidentify=False, all_in=[]):
	table = string_utils.camel_case_to_snake(table)
	if type(select) is str:
		query = "select %s from %s " % (select, table)
	elif type(select) is list:
		query = "select %s from %s " % (', '.join(select), table)
	else:
		query = "select * from %s " % table

	if where: 
		if type(where) is dict:
			where_clauses = []
			for k, v in where.items():
				if type(v) is str:
					where_clauses.append("%s = '%s'" % (k, v))
				else:
					where_clauses.append("%s = %s" % (k, v))
			query = query + "where " + " and ".join(where_clauses)
		else:
			query = query + "where %s " % where

	if where and all_in:
		query = query + "and person_id in " + str(all_in).replace('[','(').replace(']',')')
	elif all_in:
		query = query + "where person_id in " + str(all_in).replace('[','(').replace(']',')')

	if order_by:
		query = query + " order by %s " % order_by

	if limit and type(limit) in (str, int):
		query = query + " limit %s " % limit

	if offset and type(offset) in (str, int):
		query = query + " offset %s " % offset

	return raw_sql(project_id, query, 'POST', as_list, reidentify)


def match_patient(project_id, person_id, field_dict):
	person_matches = []
	match_list = []
	for table, fields in field_dict.items():
		try:
			results = get_omop(project_id, table, select=fields, where="person_id=%s" % person_id)
		except:
			pass
		else:
			if results:
				where = results[0]
				try:
					found = get_omop(project_id, table, select="person_id", where=where, as_list=True)
				except:
					pass
				else:		
					matched_ids = reduce(lambda x,y: x+y,found)
					matched_ids = [ str(mid) for mid in matched_ids]
					person_matches.append(set(matched_ids))
					match_list = list(set.intersection(*person_matches))
					match_list.remove(str(person_id))
	return match_list


def get_schema(project_id):
	headers = { 'AUTHKEY': Config.EOBO_KEY, 'Content-Type': 'application/json'}
	request_url = Config.PIANO_API + '/projects/' + project_id + '/omop/schema' 
	response = requests.get(request_url, headers=headers)
	if response.status_code in success_codes:
		return response.json()
	else:
		raise Exception("Remote query failed url: %s, EOBO authkey: %s" % (request_url, Config.EOBO_KEY))
