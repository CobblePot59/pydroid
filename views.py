from flask import render_template, request, redirect, url_for, flash
from app import app, db
#from app import Sdk, Emulator
from models import Sdk, Emulator
from pathlib import Path
import subprocess


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
            for row in my_image:
                subprocess.run('sdkmanager "'+row[0]+'"', shell=True)
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
            for row in my_image:
                subprocess.run('sdkmanager --uninstall "'+row[0]+'"', shell=True)
        flash('Your selected sdk has been removed', 'danger')
        return redirect(url_for('usdk'))
    return render_template('sdk/uninstallSDK.html', sdk=sdk)


@app.route('/createEmulator', methods=['GET', 'POST'])
def cemulator():
    installed_sdk = Sdk.query.filter_by(installed = 1).all()
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
        flash('Your emulator has been created', 'success')
        return redirect(url_for('cemulator'))
    return render_template('emulator/createEmulator.html', installed_sdk=installed_sdk)


@app.route('/removeEmulator', methods=['GET', 'POST'])
def remulator():
    emulator = Emulator.query.all()
    if request.method == 'POST':
        sname = request.form['sname']
        Emulator.query.filter_by(name=sname).delete()
        db.session.commit()
        subprocess.run('avdmanager delete avd -n '+str(sname), shell=True)
        flash('Your emulator has been removed', 'danger')
        return redirect(url_for('remulator'))
    return render_template('emulator/removeEmulator.html', emulator=emulator)


@app.route('/startEmulator', methods=['GET', 'POST'])
def semulator():
    emulator = Emulator.query.all()
    if request.method == 'POST':
        sname = request.form['sname']
        subprocess.run('emulator -writable-system -avd '+str(sname)+' -no-snapshot-load', shell=True)
        flash('Your emulator has been started', 'success')
        return redirect(url_for('semulator'))
    return render_template('emulator/startEmulator.html', emulator=emulator)
