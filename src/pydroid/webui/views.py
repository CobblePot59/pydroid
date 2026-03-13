from flask import render_template, request, redirect, url_for, flash, jsonify
from src.pydroid.webui.app import app, db
from src.pydroid.webui.models import Sdk, Emulator
from src.pydroid.webui import config
from pathlib import Path
import subprocess
import threading
import platform
import os


def _run(cmd, **kwargs):
    if config.DEBUG:
        subprocess.run(cmd, shell=True, capture_output=False, **kwargs)
    else:
        subprocess.run(cmd, shell=True, capture_output=True, **kwargs)


def _is_ajax(req):
    return req.headers.get("X-Requested-With") == "XMLHttpRequest"

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/installSDK', methods=['GET', 'POST'])
def install_sdk():
    sdk = Sdk.query.all()
    if request.method == 'POST':
        selection = request.form.getlist('checkbox')
        for checkbox in selection:
            sdk = Sdk.query.filter_by(id=checkbox).first()
            sdk.installed = 1
            db.session.commit()
            _run(f'sdkmanager "{sdk.image}"')
        flash('Your selected sdk has been installed', 'success')
        if _is_ajax(request):
            return jsonify(ok=True, redirect=url_for('install_sdk'))
        return redirect(url_for('install_sdk'))
    return render_template('sdk/installSDK.html', sdk=sdk)


@app.route('/uninstallSDK', methods=['GET', 'POST'])
def uninstall_sdk():
    sdk = Sdk.query.all()
    if request.method == 'POST':
        selection = request.form.getlist('checkbox')
        for checkbox in selection:
            sdk = Sdk.query.filter_by(id=checkbox).first()
            sdk.installed = 0
            db.session.commit()
            _run(f'sdkmanager --uninstall "{sdk.image}"')
        flash('Your selected sdk has been removed', 'error')
        if _is_ajax(request):
            return jsonify(ok=True, redirect=url_for('uninstall_sdk'))
        return redirect(url_for('uninstall_sdk'))
    return render_template('sdk/uninstallSDK.html', sdk=sdk)


@app.route('/emulator', methods=['GET'])
def get_emulator():
    installed_sdk = Sdk.query.filter_by(installed=1).all()
    emulator = Emulator.query.all()
    return render_template('emulator.html', installed_sdk=installed_sdk, emulator=emulator)


@app.route('/createEmulator', methods=['POST'])
def create_emulator():
    name = request.form['name']
    image = request.form.get('image')
    emulator = Emulator(name=str(name), image=image)
    db.session.add(emulator)
    db.session.commit()
    _run(f'echo no | avdmanager create avd -n {name} -k "{image}"')
    config_path = Path.home() / f'Android/sdk-home/.android/avd/{name}.avd/config.ini'
    with open(config_path, mode='a') as econfig:
        econfig.write('hw.keyboard=yes')
    if _is_ajax(request):
        return jsonify(ok=True, redirect=url_for('get_emulator'))
    return redirect(url_for('get_emulator'))


@app.route('/removeEmulator', methods=['POST'])
def remove_emulator():
    sname = request.form['sname']
    Emulator.query.filter_by(name=sname).delete()
    db.session.commit()
    _run(f'avdmanager delete avd -n {sname}')
    if _is_ajax(request):
        return jsonify(ok=True, redirect=url_for('get_emulator'))
    return redirect(url_for('get_emulator'))


@app.route('/startEmulator', methods=['POST'])
def start_emulator():
    sname = request.form['sname']
    threading.Thread(target=_run, args=(f'emulator -writable-system -avd "{sname}" -no-snapshot-load',), daemon=True).start()
    if _is_ajax(request):
        return jsonify(ok=True)
    return redirect(url_for('get_emulator'))

@app.route('/rootEmulator', methods=['POST'])
def root_emulator():
    sname = request.form['sname']
    q = Emulator.query.filter_by(name=sname).first()
    pimage = q.image.replace(';', '/')
    _os = platform.system()

    if _os in ('Darwin', 'Linux'):
        cmd = f'cd {os.getcwd()}/src/pydroid/modules/rootAVD-master && bash "rootAVD.sh {pimage}/ramdisk.img"'
    elif _os == 'Windows':
        cmd = f'cd {os.getcwd()}/src/pydroid/modules/rootAVD-master && cmd /c "rootAVD.bat {pimage}/ramdisk.img"'

    threading.Thread(target=_run, args=(cmd,), daemon=True).start()
    if _is_ajax(request):
        return jsonify(ok=True)
    return redirect(url_for('get_emulator'))
