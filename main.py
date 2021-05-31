#!/usr/bin/python3
# coding: utf-8

from flask import Flask, render_template, request
from pathlib import Path
from termcolor import colored
import os
import subprocess
import sqlite3
import platform
import re
import requests
import logging


app = Flask(__name__)
app.config['SECRET_KEY'] = 'deC7yngjNrcHrNtT8QqcMvKPvz22AnaZ'
log = logging.getLogger('werkzeug')
log.disabled = True


def isAdmin():
    import ctypes

    try:
        is_admin = (os.getuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


if not isAdmin():
    print(colored('Launch this app with elevated priviledges', 'red'))


sdkenv = str(Path.home()/'sdk-env')
download = str(Path.home()/'Download')
if platform.system() == 'Darwin':
    pt = 'https://dl.google.com/android/repository/platform-tools-latest-darwin.zip'
    pkg = re.findall(r"commandlinetools-mac-[\d]{7}_latest\.zip", requests.get('https://developer.android.com/studio#command-tools').text)[0]
    tools = 'https://dl.google.com/android/repository/'+pkg
    r = requests.get('https://api.github.com/repos/intel/haxm/releases/latest').json()
    pkg = r.get('assets')[-1].get('browser_download_url')
    haxm = pkg.replace('windows', 'macosx')
    _os = 'Darwin'
elif platform.system() == 'Linux':
    pt = 'https://dl.google.com/android/repository/platform-tools-latest-linux.zip'
    pkg = re.findall(r"commandlinetools-linux-[\d]{7}_latest\.zip", requests.get('https://developer.android.com/studio#command-tools').text)[0]
    tools = 'https://dl.google.com/android/repository/'+pkg
    _os = 'Linux'
elif platform.system() == 'Windows':
    pt = 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip'
    pkg = re.findall(r"commandlinetools-win-[\d]{7}_latest\.zip", requests.get('https://developer.android.com/studio#command-tools').text)[0]
    tools = 'https://dl.google.com/android/repository/'+pkg
    r = requests.get('https://api.github.com/repos/intel/haxm/releases/latest').json()
    haxm = r.get('assets')[-1].get('browser_download_url')
    r2 = requests.get('https://api.github.com/repos/google/android-emulator-hypervisor-driver-for-amd-processors/releases/latest').json()
    gvm = r2.get('assets')[-1].get('browser_download_url')
    _os = 'Windows'
    proc = platform.processor()
    hyperv = subprocess.check_output('cmd /c dism.exe /online /Get-Featureinfo /FeatureName:Microsoft-Hyper-V', encoding="437")
    hvs = 0


def dlsdk():
    from zipfile import ZipFile
    import wget
    import shutil

    if Path(sdkenv).exists() is False:
        print(colored('Please wait, sdk-env downloading...', 'yellow'))
        os.makedirs(sdkenv)
        # HYPERVISOR
        if _os == 'Darwin':
            os.makedirs(sdkenv+'/haxm')
            wget.download(haxm, download+'/haxm.zip')
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
        # PLATFORM
        os.makedirs(sdkenv+'/platforms')
        wget.download(pt, download+'/platform.zip')
        zf = ZipFile(download+'/platform.zip')
        zf.extractall(sdkenv)
        zf.close()
        os.remove(download+'/platform.zip')
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
    else:
        print(colored('sdk-env files is already present', 'green'))


def ihv():
    if _os == 'Darwin':
        try:
            cmd = subprocess.check_output('bash '+sdkenv+'/haxm/silent_install.sh -v')
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
                cmd = subprocess.check_output('cmd /c '+sdkenv+'/haxm/silent_install.bat -v')
                print(colored('haxm is installed', 'green'))
            except subprocess.CalledProcessError:
                print(colored('haxm is not installed, this step will take a little time...', 'yellow'))
                subprocess.run('cmd /c '+sdkenv+'/haxm/silent_install.bat', shell=True)
                print(colored('haxm is now installed', 'green'))
        elif Path(sdkenv+'/gvm').exists() is True:
            try:
                cmd = subprocess.check_output('cmd /c '+sdkenv+'/gvm/silent_install.bat -v')
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


def ienv():
    os.environ['ANDROID_AVD_HOME'] = str(Path.home()/'.android')
    os.environ['ANDROID_SDK_ROOT'] = sdkenv
    # os.environ['ANDROID_HOME'] = sdkenv
    if _os == 'Darwin' or _os == 'Linux':
        os.environ['PATH'] = os.environ['PATH']+':{_}/emulator:{_}/emulator/bin64:{_}/platform-tools:{_}/cmdline-tools/latest/bin'.format(_=sdkenv)
    elif _os == 'Windows':
        os.environ['PATH'] = os.environ['PATH']+';{_}\\emulator;{_}\\emulator\\bin64;{_}\\platform-tools;{_}\\cmdline-tools\\latest\\bin'.format(_=sdkenv)
    print(colored('Your environement variable has been modified', 'green'))


def isdku():
    import webbrowser

    os.makedirs(str(Path.home()/'.android/avd'), exist_ok=True)
    with open(str(Path.home()/'.android/repositories.cfg'), mode='a'):
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sdk')
def sdk():
    return render_template('sdk/sdk.html')


@app.route('/isdk', methods=['GET', 'POST'])
def isdk():
    message = ''
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    version = cur.execute('SELECT version FROM sdk;').fetchall()
    image = cur.execute('SELECT image FROM sdk;').fetchall()
    description = cur.execute('SELECT description FROM sdk;').fetchall()
    installed = cur.execute('SELECT installed FROM sdk;').fetchall()
    if request.method == 'POST':
        selection = request.form.getlist('checkbox')
        for checkbox in selection:
            cur.execute('UPDATE sdk SET installed = 1 WHERE id ='+str(checkbox))
            con.commit()
            my_image = cur.execute('SELECT image FROM sdk WHERE id ='+str(checkbox))
            for row in my_image:
                subprocess.run('sdkmanager "'+row[0]+'"', shell=True)
        con.close()
        message = 'Your selected sdk has been installed'
    return render_template('sdk/isdk.html', version=version, image=image, description=description, installed=installed, message=message)


@app.route('/usdk', methods=['GET', 'POST'])
def usdk():
    message = ''
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    version = cur.execute('SELECT version FROM sdk;').fetchall()
    image = cur.execute('SELECT image FROM sdk;').fetchall()
    description = cur.execute('SELECT description FROM sdk;').fetchall()
    installed = cur.execute('SELECT installed FROM sdk;').fetchall()
    if request.method == 'POST':
        selection = request.form.getlist('checkbox')
        for checkbox in selection:
            cur.execute('UPDATE sdk SET installed = 0 WHERE id ='+str(checkbox))
            con.commit()
            my_image = cur.execute('SELECT image FROM sdk WHERE id ='+str(checkbox))
            for row in my_image:
                subprocess.run('sdkmanager --uninstall "'+row[0]+'"', shell=True)
        con.close()
        message = 'Your selected sdk has been removed'
    return render_template('sdk/usdk.html', version=version, image=image, description=description, installed=installed, message=message)


@app.route('/emulator')
def emulator():
    return render_template('emulator/emulator.html')


@app.route('/cemulator', methods=['GET', 'POST'])
def cemulator():
    message = ''
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    image = cur.execute('SELECT image FROM sdk WHERE installed = 1;').fetchall()
    if request.method == 'POST':
        image = request.form.get('image')
        name = request.form['name']
        cur.execute('INSERT INTO emulator VALUES ("'+str(name)+'","'+str(image)+'")')
        con.commit()
        con.close()
        subprocess.run('echo no | avdmanager create avd -n '+str(name)+' -k "'+str(image)+'"', shell=True)
        print('\n')
        # with open(str(Path.home())+'/.android/avd/'+name+'.avd/config.ini', mode='a') as econfig:
        #     econfig.write('hw.keyboard=yes')
        message = 'Your emulator has been created'
    return render_template('emulator/cemulator.html', image=image, message=message)


@app.route('/remulator', methods=['GET', 'POST'])
def remulator():
    message = ''
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    name = cur.execute('SELECT name FROM emulator;').fetchall()
    image = cur.execute('SELECT image FROM emulator;').fetchall()
    if request.method == 'POST':
        sname = request.form['sname']
        cur.execute('DELETE FROM emulator WHERE name = "'+str(sname)+'"')
        con.commit()
        subprocess.run('avdmanager delete avd -n '+str(sname), shell=True)
        con.close()
        message = 'Your emulator has been removed'
    return render_template('emulator/remulator.html', name=name, image=image, message=message)


@app.route('/semulator', methods=['GET', 'POST'])
def semulator():
    message = ''
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    name = cur.execute('SELECT name FROM emulator;').fetchall()
    image = cur.execute('SELECT image FROM emulator;').fetchall()
    if request.method == 'POST':
        sname = request.form['sname']
        subprocess.run('emulator -writable-system -avd '+str(sname)+' -no-snapshot-load', shell=True)
        message = 'Your emulator has been started'
    return render_template('emulator/semulator.html', name=name, image=image, message=message)


if __name__ == '__main__':
    jdk = subprocess.run('java -version', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if jdk.returncode != 0:
        print(colored('Please verify your java installation', 'red'))
    else:
        dlsdk()
        ihv()
        ienv()
        isdku()
        app.run(host='0.0.0.0', port=80)
