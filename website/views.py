from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from flask_modals import render_template_modal
#from flask_socketio import emit
from flask.json import JSONEncoder

import json

from . import db
from . import config
#from . import socketio


from .models import Printer

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html", user = current_user)

@views.route('/AccountInfo')
@login_required
def Account():
    return render_template("AccountInfo.html", user=current_user)


@views.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user, Printer = Printer)

@views.route('/printers', methods=['GET', 'POST'])
@login_required
def printers():
    if request.method == 'POST':
        return redirect(url_for("views.printersetup"))
    return render_template('printers.html', user=current_user, Printer = Printer, display=config('basic', 'dsp_pnt_conn'))

@views.route('/printersetup', methods=['GET', 'POST'])
@login_required
def printersetup():
    if request.method == 'POST':
        ip = request.form.get('ip')
        port = request.form.get('port')
        name = request.form.get('name')
        man = request.form.get('manufacturer')
        model = request.form.get('model')
        nozzle = request.form.get('nozzel')
        heated = request.form.get('bed')
        print(heated)
        if heated == 'on':
            heated = 1
        else:
            heated = 0
        #print(f'{ip}, {port}, {name}, {man}, {model}, {nozzle}, {heated}')
        if ip == '' or port == '':
            flash('IP and Port are required', category='error')
        elif len(ip) < 7:
            flash('Invalid IP address', category='error')
        elif int(port)<1 or int(port)>65536:
            flash('Invalid Port', category='error')
        else:
            new_printer = Printer(ip, int(port), name, man, model, nozzle, heated)
            db.session.add(new_printer)
            db.session.commit()
            flash('Printer added sccessuflly', category='success')
            return redirect(url_for('views.printers'))
        
    ### run the setup script and make a handshake with printer or enter manually
    return render_template_modal('printersetup.html', user=current_user)

@views.route('/delete-printer', methods=['POST'])
def delete_printer():
    printer = json.loads(request.data)
    printerID = printer['printerID']
    printer = Printer.query.get(printerID)
    if printer:
        if current_user.user_type == 'admin':
            db.session.delete(printer)
            db.session.commit()
            flash(f'Printer: {printerID} was removed', category='success')
            return jsonify({})
        else:
            flash('Only Admins can remove printers', category='error')


'''

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Printer):
            # Convert the SQLAlchemy model object to a dictionary
            return {'id': obj.id, 'name': obj.name, 'ip': obj.ip, 'port': obj.port, 'status': obj.status, 'error': obj.error, 'manufacturer': obj.manufacturer, 'bed_temp': obj.bed_temp}
        return super(CustomJSONEncoder, self).default(obj)


@socketio.on('connect')
def handle_connect():
    # Send initial data to the client on connect
    data = Printer.query.all()
    socketio.emit('update', data, json.dumps(data, cls=CustomJSONEncoder))


@db.event.listens_for(Printer, 'after_update')
def handle_model_update(mapper, connection, target):
    # Emit a SocketIO event with the updated data
    print('wowzers')
    data = Printer.query.all()
    socketio.emit('update', data, broadcast=True)


@views.route('/socketio')
def socket():
    data = Printer.query.all()
    return render_template('socketio.html', user=current_user, data = data)
    '''