from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_toastr import Toastr 
import logging

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

toastr = Toastr(app)

log = logging.getLogger('werkzeug')
log.disabled = True

from src.pydroid.webui.views import *