from src.pydroid.setup import checkIsAdmin, checkJDK, downloadSDK, installHypervisor, installEnvironment, updateSDK, rootAVD
from src.pydroid.webui.app import app
import webbrowser

if __name__ == '__main__':
    checkIsAdmin()
    checkJDK()
    downloadSDK()
    installHypervisor()
    installEnvironment()
    updateSDK()
    rootAVD()
    webbrowser.open("http://localhost")
    app.run(host="0.0.0.0", port=80)