from termcolor import colored
from pathlib import Path
import os
import platform
import re
import requests
import subprocess
import dload


def isAdmin():
    import ctypes

    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def checkIsAdmin():
    if not isAdmin():
        print(colored('Launch this app with elevated priviledges', 'red'))
        exit()


def checkJDK():
    jdk = subprocess.run('java -version', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if jdk.returncode != 0:
        print(colored('Please verify your java installation', 'red'))
        exit()


sdkenv = str(Path.home()/'Android/sdk-env')
sdkhome = str(Path.home()/'Android/sdk-home')
download = 'tmp'
_os = platform.system()


def sdkInfo():
    if platform.system() == 'Darwin':
        url_os = 'mac'
        # HYPERVISOR
        # r = requests.get('https://api.github.com/repos/intel/haxm/releases/latest').json()
        r = requests.get('https://api.github.com/repos/intel/haxm/releases/31461850').json()
        pkg = r.get('assets')[-1].get('browser_download_url')
        haxm = pkg.replace('windows', 'macosx')
    elif platform.system() == 'Linux':
        url_os = 'linux'
    elif platform.system() == 'Windows':
        url_os = 'win'
        # HYPERVISOR
        hyperv = subprocess.check_output('cmd /c dism.exe /online /Get-Featureinfo /FeatureName:Microsoft-Hyper-V', encoding="437")

        # r = requests.get('https://api.github.com/repos/intel/haxm/releases/latest').json()
        r = requests.get('https://api.github.com/repos/intel/haxm/releases/31461850').json()
        haxm = r.get('assets')[-1].get('browser_download_url')
        r2 = requests.get('https://api.github.com/repos/google/android-emulator-hypervisor-driver-for-amd-processors/releases/latest').json()
        gvm = r2.get('assets')[-1].get('browser_download_url')

        # CMDLINE-TOOLS
        pkg = re.findall(r"commandlinetools-"+url_os+"-[\d]{8}_latest\.zip", requests.get('https://developer.android.com/studio#command-tools').text)[0]
        tools = 'https://dl.google.com/android/repository/'+pkg

    return {
        'tools': tools,
        'hyperv': hyperv,
        'haxm': haxm,
        'gvm': gvm
    }


def checkSDKenv():
    sdkPaths = [sdkenv, f'{sdkenv}/cmdline-tools', f'{sdkenv}/build-tools', f'{sdkenv}/platform-tools']

    if _os == 'Darwin':
       sdkPaths.extend([f'{sdkenv}/haxm'])
    
    if _os == 'Windows':
        sdkPaths.extend([f'{sdkenv}/hyperv', f'{sdkenv}/haxm', f'{sdkenv}/gvm'])

    for sdkPath in sdkPaths:
        if not os.path.exists(sdkPath):
            return False

    return True


def downloadSDK():
    import shutil

    if Path(sdkhome).exists() is False:
         os.makedirs(sdkhome)

    _sdkInfo = sdkInfo()
    tools = _sdkInfo['tools']
    hyperv = _sdkInfo['hyperv']
    haxm = _sdkInfo['haxm']
    gvm = _sdkInfo['gvm']

    global _build

    if checkSDKenv() is False:
        print(colored('Please wait, sdk-env downloading...', 'yellow'))
        os.makedirs(sdkenv, exist_ok=True)
        # HYPERVISOR
        if _os == 'Darwin':
            os.makedirs(sdkenv+'/haxm', exist_ok=True)
            dload.save_unzip(haxm, sdkenv+'/haxm', delete_after=True)
        elif _os == 'Windows':
            if 'Enabled' in hyperv or 'Activé' in hyperv:
                os.makedirs(sdkenv+'/hyperv', exist_ok=True)
            else:
                if 'AMD' in platform.processor():
                    os.makedirs(sdkenv+'/gvm', exist_ok=True)
                    dload.save_unzip(gvm, sdkenv+'/gvm', delete_after=True)
                else:
                    os.makedirs(sdkenv+'/haxm', exist_ok=True)
                    dload.save_unzip(haxm, sdkenv+'/haxm', delete_after=True)
        # CMDLINE-TOOLS
        os.makedirs(sdkenv+'/cmdline-tools', exist_ok=True)
        dload.save_unzip(tools, sdkenv+'/cmdline-tools', delete_after=True)
        shutil.copytree(sdkenv+'/cmdline-tools/cmdline-tools', sdkenv+'/cmdline-tools/latest', dirs_exist_ok=True)
        shutil.rmtree(sdkenv+'/cmdline-tools/cmdline-tools')
        # LICENSES
        shutil.copytree('licenses', sdkenv+'/licenses', dirs_exist_ok=True)
        # BUILD-TOOLS
        sdklist = subprocess.check_output(f'{sdkenv}/cmdline-tools/latest/bin/sdkmanager --list', shell=True, encoding="437")
        _build = sorted(re.findall(r'build-tools;(.*?)[\s\n]', sdklist), reverse=True)[0]
        subprocess.run(f'{sdkenv}/cmdline-tools/latest/bin/sdkmanager --install "build-tools;{_build}"', shell=True)
        # PLATFORM-TOOLS
        os.makedirs(sdkenv+'/platforms', exist_ok=True)
        subprocess.run(f'{sdkenv}/cmdline-tools/latest/bin/sdkmanager --install "platform-tools"', shell=True)
        print(colored('\nsdk-env files is now downloaded', 'green'))

    else:
        sdklist = subprocess.check_output(f'{sdkenv}/cmdline-tools/latest/bin/sdkmanager --list', shell=True, encoding="437")
        _build = sorted(re.findall(r'build-tools;(.*?)[\s\n]', sdklist), reverse=True)[0]
        print(colored('sdk-env files is already present', 'green'))


def installHypervisor():
    if _os == 'Darwin':
        try:
            cmd = subprocess.check_output(f'bash {sdkenv}/haxm/silent_install.sh -v', shell=True)
            print(colored('haxm is installed', 'green'))
        except subprocess.CalledProcessError:
            print(colored('haxm is not installed, this step will take a little time...', 'yellow'))
            subprocess.run(f'bash {sdkenv}/haxm/silent_install.sh', shell=True)
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
        if Path(sdkenv+'/hyperv').exists() is True:
            hvp = subprocess.check_output('cmd /c dism.exe /online /Get-Featureinfo /FeatureName:HypervisorPlatform', encoding="437")
            if 'Disabled' in hvp or 'Désactivé' in hvp:
                print(colored('HypervisorPlatform is not installed, this step will take a little time...', 'yellow'))
                subprocess.run('cmd /c dism.exe /online /Enable-Feature /FeatureName:HypervisorPlatform', shell=True)
                print(colored('HypervisorPlatform is now installed', 'green'))
        elif Path(sdkenv+'/haxm').exists() is True:
            try:
                cmd = subprocess.check_output(f'cmd /c {sdkenv}/haxm/silent_install.bat -v', encoding="437")
                print(colored('haxm is installed', 'green'))
            except subprocess.CalledProcessError:
                print(colored('haxm is not installed, this step will take a little time...', 'yellow'))
                subprocess.run(f'cmd /c {sdkenv}/haxm/silent_install.bat', shell=True)
                print(colored('haxm is now installed', 'green'))
        elif Path(sdkenv+'/gvm').exists() is True:
            try:
                cmd = subprocess.check_output(f'cmd /c {sdkenv}/gvm/silent_install.bat -v', encoding="437")
                print(colored('gvm is installed', 'green'))
            except subprocess.CalledProcessError:
                print(colored('gvm is not installed, this step will take a little time...', 'yellow'))
                subprocess.run(f'cmd /c {sdkenv}/gvm/silent_install.bat', shell=True)
                print(colored('gvm is now installed', 'green'))


def defEnvironment(variable, value1, value2):
    current_value = os.environ.get(variable)
    if current_value is None or value2 not in current_value:
        os.environ[variable] = value1
        if _os == 'Darwin' or _os == 'Linux':
            subprocess.run(f'echo \'{variable}="{value2}"\' >> /etc/profile', shell=True)
            subprocess.run('source /etc/profile', shell=True)
        if _os == 'Windows':
            subprocess.run(f'setx {variable} "{value2}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(colored(f'{variable} environment variable has been modified', 'green'))


def installEnvironment():
    os.environ['ANDROID_SDK_ROOT'] = sdkenv
    os.environ['ANDROID_SDK_HOME'] = sdkhome
    spath = os.environ['PATH']  
    
    defEnvironment('ANDROID_HOME', sdkenv, sdkenv)

    if _os == 'Darwin' or _os == 'Linux':
        upath = ':{_}/emulator:{_}/emulator/bin64:{_}/platform-tools:{_}/build-tools/{_build}:{_}/cmdline-tools/latest/bin'.format(_=sdkenv, _build=_build)
        defEnvironment('PATH', spath+upath, spath+upath)
    elif _os == 'Windows':
        import winreg

        key = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment"), "Path")[0]
        wpath = ';{_}\\emulator;{_}\\emulator\\bin64;{_}\\platform-tools;{_}\\build-tools\\{_build};{_}\\cmdline-tools\\latest\\bin'.format(_=sdkenv, _build="34")
        defEnvironment('PATH', spath+wpath, key+wpath)


def updateSDK():
    os.makedirs(f'{sdkhome}/.android/avd', exist_ok=True)
    with open(f'{sdkhome}/.android/repositories.cfg', mode='a'):
        pass

    if _os == 'Darwin' or _os == 'Linux':
        for folders, subfolders, files in os.walk(sdkenv):
            for _file in files:
                fn, ext = os.path.splitext(_file)
                if not ext:
                    _type = subprocess.check_output(f'file {folders}/{_file}', shell=True)
                    if 'executable' in _type.decode():
                        os.chmod(f'{folders}/{_file}', 0o744)
    print(colored('sdk updating...', 'yellow'))
    subprocess.run('sdkmanager --update', shell=True)
    if Path(sdkenv+'/cmdline-tools/emulator').exists() is False:
        subprocess.run('sdkmanager emulator', shell=True)
    print(colored('sdk has been updated', 'green'))
    print(colored('\nYou can now download your image to build your emulator\n', 'green'))

def rootAVD():
    dload.git_clone('https://github.com/newbit1/rootAVD.git', clone_dir='./modules')
    if _os == 'Darwin' or _os == 'Linux':
        os.chmod('./modules/rootAVD-master/rootAVD.sh', 0o744)