import os

PIANO_API = os.getenv('PIANO_API', "http://dev.api.evidentli.com")


class Config(object):
    """
    Base Configuration
    """
    SECRET_KEY = os.getenv('SECRET_KEY', "piano")

    PIANO_API = PIANO_API
