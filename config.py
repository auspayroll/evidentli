import os

"""
Base Configuration
"""
DEBUG = False
TESTING = False
CORS = False
EOBO_KEY = os.getenv('EOBO_KEY', 'eobo')
SECRET_KEY = os.getenv('SECRET_KEY', "piano")
PIANO_API = os.getenv('PIANO_API', "http://dev.api.evidentli.com")

try:
	from local_config import *
except:
	pass


class Config(object):
    DEBUG = DEBUG
    TESTING = TESTING
    CORS = CORS
    EOBO_KEY = EOBO_KEY
    SECRET_KEY = SECRET_KEY
    PIANO_API = PIANO_API