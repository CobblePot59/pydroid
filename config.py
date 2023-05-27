from datetime import timedelta
from os import path

SECRET_KEY = 'deC7yngjNrcHrNtT8QqcMvKPvz22AnaZ'
PERMANENT_SESSION_LIFETIME =  timedelta(minutes=15)
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.abspath('db/pydroid.db')
