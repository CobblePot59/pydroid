from src.pydroid.webui import config
from pathlib import Path
from git import Repo
import os
import platform
import re
import requests
import subprocess
import zipfile
import io
import shutil
import winreg

sdkenv = str(Path.home() / 'Android/sdk-env')
sdkhome = str(Path.home() / 'Android/sdk-home')
_os = platform.system()
_build = None


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

_COLORS = {
    'info':    '\033[0m',
    'success': '\033[32m',
    'warning': '\033[33m',
    'error':   '\033[31m',
    'step':    '\033[36m',
}


def _log(level, msg):
    if level == 'info' and not config.DEBUG:
        return
    print(f"{_COLORS.get(level, '')}{msg}\033[0m")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def isAdmin():
    import ctypes
    try:
        return os.getuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def checkIsAdmin():
    if not isAdmin():
        _log('error', 'This script requires elevated privileges.')
        exit()


def _run(cmd, **kwargs):
    return subprocess.run(cmd, shell=True, capture_output=True, **kwargs)


def checkJDK():
    result = _run('java -version')
    if result.returncode != 0:
        _log('error', 'Java not found. Please verify your JDK installation.')
        exit()


def save_unzip(url, dest_dir):
    _log('info', f'Downloading {url}')
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(dest_dir)


def git_clone(url, clone_dir='.'):
    Repo.clone_from(url, clone_dir)


def detect_pkg_manager():
    for pm in ('apt-get', 'dnf'):
        if _run(f'which {pm}').returncode == 0:
            return pm
    return None


# ---------------------------------------------------------------------------
# SDK
# ---------------------------------------------------------------------------

def sdkInfo():
    url_os = {'Darwin': 'mac', 'Linux': 'linux', 'Windows': 'win'}[_os]
    pkg = re.findall(r"commandlinetools-" + url_os + r"-[\d]{8}_latest\.zip", requests.get('https://developer.android.com/studio#command-tools').text)[0]
    return {'tools': 'https://dl.google.com/android/repository/' + pkg}


def checkSDKenv():
    paths = [sdkenv, f'{sdkenv}/cmdline-tools', f'{sdkenv}/build-tools', f'{sdkenv}/platform-tools']
    return all(os.path.exists(p) for p in paths)


def downloadSDK():
    global _build
    os.makedirs(sdkhome, exist_ok=True)

    _log('step', '[*] SDK Environment')

    if not checkSDKenv():
        tools = sdkInfo()['tools']
        _log('info', 'SDK environment not found, downloading...')
        os.makedirs(sdkenv, exist_ok=True)

        os.makedirs(sdkenv + '/cmdline-tools', exist_ok=True)
        save_unzip(tools, sdkenv + '/cmdline-tools')
        shutil.copytree(sdkenv + '/cmdline-tools/cmdline-tools', sdkenv + '/cmdline-tools/latest', dirs_exist_ok=True)
        shutil.rmtree(sdkenv + '/cmdline-tools/cmdline-tools')

        if _os in ('Darwin', 'Linux'):
            os.chmod(f'{sdkenv}/cmdline-tools/latest/bin/sdkmanager', 0o744)

        shutil.copytree('src/pydroid/licenses', sdkenv + '/licenses', dirs_exist_ok=True)

        sdklist = _run(f'{sdkenv}/cmdline-tools/latest/bin/sdkmanager --list', text=True).stdout

        _build = sorted(re.findall(r'build-tools;(.*?)[\s\n]', sdklist), reverse=True)[0]
        _log('info', f'Installing build-tools {_build}')
        _run(f'{sdkenv}/cmdline-tools/latest/bin/sdkmanager --install "build-tools;{_build}"')

        os.makedirs(sdkenv + '/platforms', exist_ok=True)
        _log('info', 'Installing platform-tools')
        _run(f'{sdkenv}/cmdline-tools/latest/bin/sdkmanager --install "platform-tools"')

        _log('success', 'SDK environment ready')
    else:
        sdklist = _run(f'{sdkenv}/cmdline-tools/latest/bin/sdkmanager --list', text=True).stdout
        _build = sorted(re.findall(r'build-tools;(.*?)[\s\n]', sdklist), reverse=True)[0]
        _log('success', 'SDK environment already present')


# ---------------------------------------------------------------------------
# Hypervisor
# ---------------------------------------------------------------------------

def installHypervisor():
    _log('step', '[*] Hypervisor')

    if _os == 'Darwin':
        _log('success', 'Hypervisor.Framework is built-in on macOS — nothing to install')

    elif _os == 'Linux':
        cpu_virt = _run('egrep -c "(vmx|svm)" /proc/cpuinfo', text=True)
        if cpu_virt.stdout.strip() == '0':
            _log('warning', 'CPU may not support hardware virtualization (vmx/svm not found)')

        pm = detect_pkg_manager()
        if pm is None:
            _log('error', 'No supported package manager found (apt-get or dnf)')
            return

        kvm_installed = _run('which qemu-kvm').returncode == 0
        if not kvm_installed:
            _log('info', f'Installing KVM via {pm}')
            if pm == 'apt-get':
                _run('apt-get install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils')
            elif pm == 'dnf':
                _run('dnf install -y qemu-kvm libvirt libvirt-client bridge-utils')
                _run('systemctl enable --now libvirtd')
            _log('success', 'KVM installed')
        else:
            _log('success', 'KVM already installed')

    elif _os == 'Windows':
        _log('info', 'Checking Windows Hypervisor Platform (WHPX)')
        ps_cmd = 'powershell -Command "(Get-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform).State"'
        result = _run(ps_cmd, text=True)
        state = result.stdout.strip()

        if state == 'Enabled':
            _log('success', 'WHPX is already enabled')
        else:
            _log('info', 'WHPX not enabled, enabling now...')
            enable = _run('cmd /c dism.exe /online /Enable-Feature /FeatureName:HypervisorPlatform /NoRestart')
            if enable.returncode in (0, 3010):
                _log('warning', 'WHPX enabled — a system reboot is required to apply changes')
            else:
                _log('error', 'Failed to enable WHPX. Ensure virtualization is active in BIOS and Windows 10 1803+ is installed.')


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

def defEnvironment(variable, value1, value2):
    current_value = os.environ.get(variable)
    if current_value is None or value2 not in current_value:
        os.environ[variable] = value1

        if _os in ('Darwin', 'Linux'):
            profile = open('/etc/profile').read()
            if value2 not in profile:
                _run(f'echo \'{variable}="${{variable}}{value2}"\' >> /etc/profile')
                _run('source /etc/profile')      

        if _os == 'Windows':
            try:
                reg_value = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment'), variable)[0]
            except FileNotFoundError:
                reg_value = ''

            if value2 not in reg_value:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_SET_VALUE | winreg.KEY_CREATE_SUB_KEY)
                winreg.SetValueEx(key, variable, 0, winreg.REG_SZ, reg_value + value2)
                winreg.CloseKey(key)

    _log('success', f'{variable} set')

def installEnvironment():
    _log('step', '[*] Environment Variables')
    spath = os.environ.get('PATH', '')

    defEnvironment('ANDROID_HOME', sdkenv, sdkenv)
    defEnvironment('ANDROID_SDK_ROOT', sdkenv, sdkenv)
    defEnvironment('ANDROID_SDK_HOME', sdkhome, sdkhome)

    if _os in ('Darwin', 'Linux'):
        upath = ':{_}/emulator:{_}/emulator/bin64:{_}/platform-tools:{_}/build-tools/{b}:{_}/cmdline-tools/latest/bin'.format(_=sdkenv, b=_build)
        defEnvironment('PATH', spath + upath, upath)
    elif _os == 'Windows':
        key = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment'), 'Path')[0]
        wpath = ';{_}\\emulator;{_}\\emulator\\bin64;{_}\\platform-tools;{_}\\build-tools\\{b};{_}\\cmdline-tools\\latest\\bin'.format(_=sdkenv, b=_build)
        defEnvironment('PATH', spath + wpath, wpath)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def updateSDK():
    _log('step', '[*] SDK Update')
    os.makedirs(f'{sdkhome}/.android/avd', exist_ok=True)
    with open(f'{sdkhome}/.android/repositories.cfg', mode='a'):
        pass

    if _os in ('Darwin', 'Linux'):
        for folders, _, files in os.walk(sdkenv):
            for _file in files:
                _, ext = os.path.splitext(_file)
                if not ext:
                    _type = _run(f'file {folders}/{_file}', text=True).stdout
                    if 'executable' in _type.decode():
                        os.chmod(f'{folders}/{_file}', 0o744)

    _run('sdkmanager --update')

    if not Path(sdkenv + '/cmdline-tools/emulator').exists():
        _run('sdkmanager emulator')

    _log('success', 'SDK packages up to date')

    _log('step', '[*] Hardware Acceleration')
    accel = _run(f'{sdkenv}/emulator/emulator -accel-check', text=True)
    for line in accel.stdout.splitlines():
        line = line.strip()
        if not line or line in ('accel:', 'accel') or line.isdigit():
            continue
        if 'usable' in line:
            _log('success', line)
        elif 'not' in line.lower():
            _log('warning', line)
        else:
            _log('info', line)

# ---------------------------------------------------------------------------
# Misc
# ---------------------------------------------------------------------------

def rootAVD():
    _log('step', '[*] Modules')
    if Path('./src/pydroid/modules/rootAVD-master').exists():
        _log('success', 'rootAVD already present')
    else:
        _log('info', 'Cloning rootAVD...')
        git_clone('https://github.com/newbit1/rootAVD.git', clone_dir='./src/pydroid/modules/rootAVD-master')
        _log('success', 'rootAVD module is installed')

    if _os in ('Darwin', 'Linux'):
        os.chmod('./src/pydroid/modules/rootAVD-master/rootAVD.sh', 0o744)
