from views import app
from app import downloadSDK, installHypervisor, installEnvironment, updateSDK
from termcolor import colored
import subprocess


if __name__ == '__main__':
    jdk = subprocess.run('java -version', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if jdk.returncode != 0:
        print(colored('Please verify your java installation', 'red'))
    else:
        downloadSDK()
        installHypervisor()
        installEnvironment()
        updateSDK()
        app.run(host='0.0.0.0', port=80)
