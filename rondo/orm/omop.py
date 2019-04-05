import requests
import json
from functools import reduce
from config import PIANO_API


def get_omop(table, select=None, where=None, order_by=None, 
	limit=None, offset=None, as_list=False, reidentify=False):

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

	if order_by:
		query = query + " order by %s " % order_by

	if limit and type(limit) in (str, int):
		query = query + " limit %s " % limit

	if offset and type(offset) in (str, int):
		query = query + " offset %s " % offset

	payload = { "query": query, "reidentify": reidentify }
	if as_list:
		payload["format"] = "list"


	headers = { 'AUTHKEY': 'eobo', 'Content-Type': 'application/json'}

	response = requests.post(PIANO_API + '/projects/test_michael2/omop', 
    	json=payload, headers=headers)
	rows = response.json()['rows']
	return rows


def _get_match_dict(fields):
	kw = {}
	keywords = [x.strip().strip(",") for x in fields.split(' ')]
	for keyword in keywords:
		try:
			table, field = keyword.split('.')
		except:
			pass
		else:
			table_fields = kw.setdefault(table.lower(),[])
			table_fields.append(field.lower())
	return kw


def match_patient(person_id, fields):
	fields = _get_match_dict(fields)
	print(fields)
	person_matches = []
	for table, fields in fields.items():
		try:
			results = get_omop(table, select=fields, where="person_id=%s" % person_id)
		except:
			pass
		else:
			if results:
				where = results[0]
				try:
					found = get_omop(table, select="person_id", where=where, as_list=True)
				except:
					pass
				else:
					matched_ids = reduce(lambda x,y: x+y,found)
					person_matches.append(set(matched_ids))

	match_list = list(set.intersection(*person_matches))
	match_list.remove(person_id)
	return match_list



