from flask import Flask
app = Flask(__name__)
app.config.from_object('config.Config')
import rondo.views
from .rondo_model import Rondo
