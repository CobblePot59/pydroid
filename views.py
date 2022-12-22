from flask import Flask, render_template, request
import logging
import sqlite3
import subprocess


app = Flask(__name__)
app.config['SECRET_KEY'] = 'deC7yngjNrcHrNtT8QqcMvKPvz22AnaZ'
log = logging.getLogger('werkzeug')
log.disabled = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/installSDK', methods=['GET', 'POST'])
def isdk():
    message = ''
    con = sqlite3.connect('db/database.db')
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
    return render_template('sdk/installSDK.html', version=version, image=image, description=description, installed=installed, message=message)


@app.route('/uninstallSDK', methods=['GET', 'POST'])
def usdk():
    message = ''
    con = sqlite3.connect('db/database.db')
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
    return render_template('sdk/uninstallSDK.html', version=version, image=image, description=description, installed=installed, message=message)


@app.route('/createEmulator', methods=['GET', 'POST'])
def cemulator():
    message = ''
    con = sqlite3.connect('db/database.db')
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
    return render_template('emulator/createEmulator.html', image=image, message=message)


@app.route('/removeEmulator', methods=['GET', 'POST'])
def remulator():
    message = ''
    con = sqlite3.connect('db/database.db')
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
    return render_template('emulator/removeEmulator.html', name=name, image=image, message=message)


@app.route('/startEmulator', methods=['GET', 'POST'])
def semulator():
    message = ''
    con = sqlite3.connect('db/database.db')
    cur = con.cursor()
    name = cur.execute('SELECT name FROM emulator;').fetchall()
    image = cur.execute('SELECT image FROM emulator;').fetchall()
    if request.method == 'POST':
        sname = request.form['sname']
        subprocess.run('emulator -writable-system -avd '+str(sname)+' -no-snapshot-load', shell=True)
        message = 'Your emulator has been started'
    return render_template('emulator/startEmulator.html', name=name, image=image, message=message)