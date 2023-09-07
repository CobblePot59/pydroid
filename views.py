from flask import render_template, request, redirect, url_for, flash
from app import app, db
from models import Sdk, Emulator
from pathlib import Path
import subprocess
import threading
import platform
import os


def run_background_command(command):
    subprocess.Popen(command, shell=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/installSDK', methods=['GET', 'POST'])
def install_sdk():
    sdk = Sdk.query.all()
    if request.method == 'POST':
        selection = request.form.getlist('checkbox')
        for checkbox in selection:
            sdk = Sdk.query.filter_by(id = checkbox).first()
            sdk.installed = 1
            db.session.commit()
            my_image = sdk.image
            subprocess.run('sdkmanager "'+my_image+'"', shell=True)
        flash('Your selected sdk has been installed', 'success')
        return redirect(url_for('install_sdk'))
    return render_template('sdk/installSDK.html', sdk=sdk)


@app.route('/uninstallSDK', methods=['GET', 'POST'])
def uninstall_sdk():
    sdk = Sdk.query.all()
    if request.method == 'POST':
        selection = request.form.getlist('checkbox')
        for checkbox in selection:
            sdk = Sdk.query.filter_by(id = checkbox).first()
            sdk.installed = 0
            db.session.commit()
            my_image = sdk.image
            subprocess.run('sdkmanager --uninstall "'+my_image+'"', shell=True)
        flash('Your selected sdk has been removed', 'danger')
        return redirect(url_for('uninstall_sdk'))
    return render_template('sdk/uninstallSDK.html', sdk=sdk)


@app.route('/emulator', methods=['GET'])
def get_emulator():
    installed_sdk = Sdk.query.filter_by(installed = 1).all()
    emulator = Emulator.query.all()
    return render_template('emulator.html', installed_sdk=installed_sdk, emulator=emulator)


@app.route('/createEmulator', methods=['POST'])
def create_emulator():
    name = request.form['name']
    image = request.form.get('image')
    emulator = Emulator(name = str(name), image = image)
    db.session.add(emulator)
    db.session.commit()
    subprocess.run('echo no | avdmanager create avd -n '+str(name)+' -k "'+str(image)+'"', shell=True)
    print('\n')
    with open(str(Path.home())+'/Android/sdk-home/.android/avd/'+str(name)+'.avd/config.ini', mode='a') as econfig:
        econfig.write('hw.keyboard=yes')
    return redirect(url_for('get_emulator'))


@app.route('/removeEmulator', methods=['POST'])
def remove_emulator():
    sname = request.form['sname']
    Emulator.query.filter_by(name=sname).delete()
    db.session.commit()
    subprocess.run('avdmanager delete avd -n '+str(sname), shell=True)
    return redirect(url_for('get_emulator'))


@app.route('/startEmulator', methods=['POST'])
def start_emulator():
    sname = request.form['sname']
    background_thread = threading.Thread(target=run_background_command, args=(f'emulator -writable-system -avd "{sname}" -no-snapshot-load',))
    background_thread.start()
    return redirect(url_for('get_emulator'))


@app.route('/rootEmulator', methods=['POST'])
def root_emulator():
    sname = request.form['sname']
    q = Emulator.query.filter_by(name=sname).first()
    pimage = q.image.replace(';', '/')
    _os = platform.system()

    if _os == 'Darwin' or _os == 'Linux':
        background_thread = threading.Thread(target=run_background_command, args=(f'cd {os.getcwd()}/modules/rootAVD-master && bash "rootAVD.sh {pimage}/ramdisk.img"',))
    elif _os == 'Windows':
        background_thread = threading.Thread(target=run_background_command, args=(f'cd {os.getcwd()}/modules/rootAVD-master && cmd /c "rootAVD.bat {pimage}/ramdisk.img"',))

    background_thread.start()
    return redirect(url_for('get_emulator'))


# https://github.com/CobblePot59/android/tree/main

# @app.route('/addCA', methods=['POST'])
# def add_CA():
#     sname = request.form['sname']
#     background_thread = threading.Thread(target=run_background_command, args=(f'',))
#     background_thread.start()
#     return redirect(url_for('get_emulator'))


# @app.route('/addFrida', methods=['POST'])
# def add_Frida():
#     sname = request.form['sname']
#     background_thread = threading.Thread(target=run_background_command, args=(f'',))
#     background_thread.start()
#     return redirect(url_for('get_emulator'))