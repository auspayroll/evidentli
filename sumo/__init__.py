from flask import Flask
app = Flask(__name__)
app.config.from_object('config.Config')
from .sumo_model import Sumo
import sumo.views
