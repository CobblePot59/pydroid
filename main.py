from views import app
from app import downloadSDK, installHypervisor, installEnvironment, updateSDK


if __name__ == '__main__':
    downloadSDK()
    installHypervisor()
    installEnvironment()
    updateSDK()
    app.run(host='0.0.0.0', port=80)
