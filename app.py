from termcolor import colored
from pathlib import Path
import os
import platform
import re
import requests
import subprocess


def isAdmin():
    import ctypes

    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin

if not isAdmin():
    print(colored('Launch this app with elevated priviledges', 'red'))
    exit()

jdk = subprocess.run('java -version', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if jdk.returncode != 0:
    print(colored('Please verify your java installation', 'red'))
    exit()


sdkenv = str(Path.home()/'Android/sdk-env')
sdkhome = str(Path.home()/'Android/sdk-home')
download = 'tmp'

if platform.system() == 'Darwin':
    # CMDLINE-TOOLS
    pkg = re.findall(r"commandlinetools-mac-[\d]{7}_latest\.zip", requests.get('https://developer.android.com/studio#command-tools').text)[0]
    tools = 'https://dl.google.com/android/repository/'+pkg
    # HYPERVISOR
    r = requests.get('https://api.github.com/repos/intel/haxm/releases/latest').json()
    pkg = r.get('assets')[-1].get('browser_download_url')
    haxm = pkg.replace('windows', 'macosx')
    _os = 'Darwin'
elif platform.system() == 'Linux':
    # CMDLINE-TOOLS
    pkg = re.findall(r"commandlinetools-linux-[\d]{7}_latest\.zip", requests.get('https://developer.android.com/studio#command-tools').text)[0]
    tools = 'https://dl.google.com/android/repository/'+pkg
    _os = 'Linux'
elif platform.system() == 'Windows':
    # CMDLINE-TOOLS
    pkg = re.findall(r"commandlinetools-win-[\d]{7}_latest\.zip", requests.get('https://developer.android.com/studio#command-tools').text)[0]
    tools = 'https://dl.google.com/android/repository/'+pkg
    # HYPERVISOR
    hvs = 0
    hyperv = subprocess.check_output('cmd /c dism.exe /online /Get-Featureinfo /FeatureName:Microsoft-Hyper-V', encoding="437")
    proc = platform.processor()

    r = requests.get('https://api.github.com/repos/intel/haxm/releases/latest').json()
    haxm = r.get('assets')[-1].get('browser_download_url')
    r2 = requests.get('https://api.github.com/repos/google/android-emulator-hypervisor-driver-for-amd-processors/releases/latest').json()
    gvm = r2.get('assets')[-1].get('browser_download_url')
    _os = 'Windows'
        

def downloadSDK():
    from zipfile import ZipFile
    import wget
    import shutil

    if Path(sdkhome).exists() is False:
         os.makedirs(sdkhome)

    if Path(sdkenv).exists() is False:
        print(colored('Please wait, sdk-env downloading...', 'yellow'))
        os.makedirs(sdkenv)
        # HYPERVISOR
        if _os == 'Darwin':
            os.makedirs(sdkenv+'/haxm')
            wget.download(haxm, download+'/haxm.zip')
            open(download+'/haxm.zip', 'wb').write(requests.get(haxm).content)
            zf = ZipFile(download+'/haxm.zip')
            zf.extractall(sdkenv+'/haxm')
            zf.close()
            os.remove(download+'/haxm.zip')
        elif _os == 'Windows':
            global hvs
            if 'Enabled' in hyperv or 'Activé' in hyperv:
                hvs = 1
            else:
                if 'AMD' in proc:
                    os.makedirs(sdkenv+'/gvm')
                    wget.download(gvm, download+'/gvm.zip')
                    zf = ZipFile(download+'/gvm.zip')
                    zf.extractall(sdkenv+'/gvm')
                    zf.close()
                    os.remove(download+'/gvm.zip')
                else:
                    os.makedirs(sdkenv+'/haxm')
                    wget.download(haxm, download+'/haxm.zip')
                    zf = ZipFile(download+'/haxm.zip')
                    zf.extractall(sdkenv+'/haxm')
                    zf.close()
                    os.remove(download+'/haxm.zip')
        # CMDLINE-TOOLS
        os.makedirs(sdkenv+'/cmdline-tools')
        wget.download(tools, download+'/tools.zip')
        zf = ZipFile(download+'/tools.zip')
        zf.extractall(sdkenv+'/cmdline-tools')
        zf.close()
        os.remove(download+'/tools.zip')
        os.rename(sdkenv+'/cmdline-tools/cmdline-tools', sdkenv+'/cmdline-tools/latest')
        # LICENSES
        shutil.copytree('licenses', sdkenv+'/licenses')
        print(colored('\nsdk-env files is now downloaded', 'green'))
        # BUILD-TOOLS
        sdklist = subprocess.check_output(f'{sdkenv}/cmdline-tools/latest/bin/sdkmanager --list', shell=True, encoding="437")
        global _build
        _build = sorted(re.findall(r'build-tools;(.*?)[\s\n]', sdklist), reverse=True)[0]
        subprocess.run(f'{sdkenv}/cmdline-tools/latest/bin/sdkmanager --install "build-tools;{_build}"', shell=True)
        # PLATFORM-TOOLS
        os.makedirs(sdkenv+'/platforms')
        subprocess.run(f'{sdkenv}/cmdline-tools/latest/bin/sdkmanager --install "platform-tools"', shell=True)  

    else:
        sdklist = subprocess.check_output(f'{sdkenv}/cmdline-tools/latest/bin/sdkmanager --list', shell=True, encoding="437")
        global _build
        _build = sorted(re.findall(r'build-tools;(.*?)[\s\n]', sdklist), reverse=True)[0]
        print(colored('sdk-env files is already present', 'green'))


def installHypervisor():
    if _os == 'Darwin':
        try:
            cmd = subprocess.check_output('bash '+sdkenv+'/haxm/silent_install.sh -v', shell=True)
            print(colored('haxm is installed', 'green'))
        except subprocess.CalledProcessError:
            print(colored('haxm is not installed, this step will take a little time...', 'yellow'))
            subprocess.run('bash '+sdkenv+'/haxm/silent_install.sh', shell=True)
            print(colored('haxm is now installed', 'green'))
    elif _os == 'Linux':
        cmd = subprocess.run('dpkg -l | grep qemu-kvm', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if cmd.returncode == 1:
            print(colored('qemu is not installed, processing...', 'yellow'))
            subprocess.run('apt -y install qemu-kvm', shell=True)
            print(colored('qemu is now installed', 'green'))
        else:
            print(colored('qemu is installed', 'green'))
    elif _os == 'Windows':
        if Path(sdkenv+'/haxm').exists() is True:
            try:
                cmd = subprocess.check_output('cmd /c '+sdkenv+'/haxm/silent_install.bat -v', encoding="437")
                print(colored('haxm is installed', 'green'))
            except subprocess.CalledProcessError:
                print(colored('haxm is not installed, this step will take a little time...', 'yellow'))
                subprocess.run('cmd /c '+sdkenv+'/haxm/silent_install.bat', shell=True)
                print(colored('haxm is now installed', 'green'))
        elif Path(sdkenv+'/gvm').exists() is True:
            try:
                cmd = subprocess.check_output('cmd /c '+sdkenv+'/gvm/silent_install.bat -v', encoding="437")
                print(colored('gvm is installed', 'green'))
            except subprocess.CalledProcessError:
                print(colored('gvm is not installed, this step will take a little time...', 'yellow'))
                subprocess.run('cmd /c '+sdkenv+'/gvm/silent_install.bat', shell=True)
                print(colored('gvm is now installed', 'green'))
        elif hvs == 1:
            hvp = subprocess.check_output('cmd /c dism.exe /online /Get-Featureinfo /FeatureName:HypervisorPlatform', encoding="437")
            if 'Disabled' in hvp or 'Désactivé' in hvp:
                print(colored('HypervisorPlatform is not installed, this step will take a little time...', 'yellow'))
                subprocess.run('cmd /c dism.exe /online /Enable-Feature /FeatureName:HypervisorPlatform', shell=True)
                print(colored('HypervisorPlatform is now installed', 'green'))


def installEnvironment():
    
    os.environ['ANDROID_SDK_ROOT'] = sdkenv
    os.environ['ANDROID_SDK_HOME'] = sdkhome
    spath = os.environ['PATH']

    if _os == 'Darwin' or _os == 'Linux':
        upath = ':{_}/emulator:{_}/emulator/bin64:{_}/platform-tools:{_}/build-tools/{_build}:{_}/cmdline-tools/latest/bin'.format(_=sdkenv, _build=_build)
        if not upath in os.environ['PATH']:
            os.environ['PATH'] = spath+upath
            subprocess.run('echo \'PATH="'+spath+upath+'"\' >> /etc/profile', shell=True)
            subprocess.run('source /etc/profile', shell=True)
    elif _os == 'Windows':
        import winreg

        key = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment"), "Path")[0]
        wpath = ';{_}\\emulator;{_}\\emulator\\bin64;{_}\\platform-tools;{_}\\build-tools\\{_build};{_}\\cmdline-tools\\latest\\bin'.format(_=sdkenv, _build=_build)
        if not wpath in os.environ['PATH']:
            os.environ['PATH'] = spath+wpath
            subprocess.run('setx PATH "'+key+wpath+'"', shell=True)
    print(colored('Your environement variable has been modified', 'green'))


def updateSDK():
    import webbrowser

    os.makedirs(str(sdkhome)+'/.android/avd', exist_ok=True)
    with open(str(sdkhome)+'/.android/repositories.cfg', mode='a'):
        pass

    if _os == 'Darwin' or _os == 'Linux':
        for folders, subfolders, files in os.walk(sdkenv):
            for _file in files:
                fn, ext = os.path.splitext(_file)
                if not ext:
                    _type = subprocess.check_output('file '+folders+'/'+_file, shell=True)
                    if 'executable' in _type.decode():
                        os.chmod(folders+'/'+_file, 0o744)
    print(colored('sdk updating...', 'yellow'))
    subprocess.run('sdkmanager --update', shell=True)
    if Path(sdkenv+'/cmdline-tools/emulator').exists() is False:
        subprocess.run('sdkmanager emulator', shell=True)
    print(colored('sdk has been updated', 'green'))
    print(colored('\nYou can now download your image to build your emulator\n', 'green'))

    webbrowser.open("http://localhost")
