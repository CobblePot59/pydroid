from src.pydroid.setup import checkIsAdmin, checkJDK, downloadSDK, installHypervisor, installEnvironment, updateSDK, rootAVD
from src.pydroid.webui.app import app
from src.pydroid.webui import config
import logging
import flask.cli
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    config.DEBUG = args.debug

    checkIsAdmin()
    checkJDK()
    downloadSDK()
    installHypervisor()
    installEnvironment()
    updateSDK()
    rootAVD()

    print(f'\033[32m\nSetup complete! You can now create your emulators at: http://127.0.0.1:5000\033[0m\n')    

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    flask.cli.show_server_banner = lambda *x: None
    app.run(host="127.0.0.1", port=5000)
