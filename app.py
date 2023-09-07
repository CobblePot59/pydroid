from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
from setup import checkIsAdmin, checkJDK, sdkInfo, downloadSDK, installHypervisor, installEnvironment, updateSDK, rootAVD
import webbrowser

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

log = logging.getLogger('werkzeug')
log.disabled = True

from views import *

if __name__ == '__main__':
    checkIsAdmin()
    checkJDK()
    downloadSDK()
    installHypervisor()
    installEnvironment()
    updateSDK()
    rootAVD()
    webbrowser.open("http://localhost")
    app.run(host='0.0.0.0', port=80)
