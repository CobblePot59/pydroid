from flask import render_template, request, redirect, url_for, flash
from app import app, db
from models import Sdk, Emulator
from pathlib import Path
import subprocess
import threading


def run_background_command(command):
    subprocess.Popen(command, shell=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/installSDK', methods=['GET', 'POST'])
def isdk():
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
        return redirect(url_for('isdk'))
    return render_template('sdk/installSDK.html', sdk=sdk)


@app.route('/uninstallSDK', methods=['GET', 'POST'])
def usdk():
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
        return redirect(url_for('usdk'))
    return render_template('sdk/uninstallSDK.html', sdk=sdk)


@app.route('/emulator', methods=['GET', 'POST'])
def emulator():
    installed_sdk = Sdk.query.filter_by(installed = 1).all()
    emulator = Emulator.query.all()
    return render_template('emulator.html', installed_sdk=installed_sdk, emulator=emulator)

@app.route('/createEmulator', methods=['POST'])
def cemulator():
    if request.method == 'POST':
        name = request.form['name']
        image = request.form.get('image')
        emulator = Emulator(name = str(name), image = image)
        db.session.add(emulator)
        db.session.commit()
        subprocess.run('echo no | avdmanager create avd -n '+str(name)+' -k "'+str(image)+'"', shell=True)
        print('\n')
        with open(str(Path.home())+'/Android/sdk-home/.android/avd/'+str(name)+'.avd/config.ini', mode='a') as econfig:
            econfig.write('hw.keyboard=yes')
        return redirect(url_for('emulator'))


@app.route('/removeEmulator', methods=['POST'])
def remulator():
    if request.method == 'POST':
        sname = request.form['sname']
        Emulator.query.filter_by(name=sname).delete()
        db.session.commit()
        subprocess.run('avdmanager delete avd -n '+str(sname), shell=True)
        return redirect(url_for('emulator'))


@app.route('/startEmulator', methods=['POST'])
def semulator():
    if request.method == 'POST':
        sname = request.form['sname']
        background_thread = threading.Thread(target=run_background_command, args=(f'emulator -writable-system -avd "{sname}" -no-snapshot-load',))
        background_thread.start()
        return redirect(url_for('emulator'))
