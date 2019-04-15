import requests
from config import Config

PROJECTS_URL = Config.PIANO_API + '/projects'


def save_config(project_id, config_name, payload):
    response = requests.post(PROJECTS_URL + '/%s/%s' % (project_id, config_name), json=[payload])
    if response.status_code == requests.codes.ok:
        jsn = response.json()
        if type(jsn) is list:
            return jsn[0]
        else:
            return jsn


def get_config(project_id, config_name, config_id):
    response = requests.get(PROJECTS_URL + '/%s/%s/%s' % (project_id, config_name, config_id))
    if response.status_code == requests.codes.ok:
        jsn = response.json()
        if type(jsn) is list:
            return jsn[0]
        else:
            return jsn


def get_configs(project_id, config_name):
    response = requests.get(PROJECTS_URL + '/%s/%s' % (project_id, config_name))
    if response.status_code == requests.codes.ok:
        jsn = response.json()
        return jsn

def get_configs_in(project_id, config_name, field, field_list):
    field_list_vals = [ str(ids) for ids in field_list]
    response = requests.get(PROJECTS_URL + '/%s/%s?query=%s=in%s' % (project_id, config_name, field, field_list_vals))
    if response.status_code == requests.codes.ok:
        jsn = response.json()
        return jsn


def query_config(project_id, config_name, query):
    terms = {}
    for (k,v) in query.items():
        try:
            kval, operator = k.split('__')
        except:
            if type(v) is list:
                terms[k] = str(k) + "=in[" + ", ".join([ "'%s'" % sv for sv in v ]) + "]"
            else:
                terms[k] = "%s='%s'" % (k, v)
        else: 

            if 'lt' == operator:
                terms[k] = "%s<'%s'" % (kval, v)
            elif 'lte' == operator:
                terms[k] = "%s<='%s'" % (kval, v)
            elif 'gt' == operator:
                terms[k] = "%s>'%s'" % (kval, v)
            elif 'gte' == operator:
                terms[k] = "%s>='%s'" % (kval, v)

            

    querystring = ";".join(terms.values())
    request_string = PROJECTS_URL + "/%s/%s?query=AND(%s)" % (project_id, config_name, querystring)
    response = requests.get(request_string)
    if response.status_code == 200 and response.content:
        return response.json()
