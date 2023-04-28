from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy.sql import func
from . import db
from .models import User, Printer, APIKEY
import json

api = Blueprint('api', __name__)

### printers

'http://127.0.0.1:5000/api/printers?pnt=ALL'
@api.route('/api/printers', methods=['GET'])
def query_database():
    arg = request.args.get('pnt')
    if arg == 'ALL':
        printers = {}
        for item in Printer.query.all():
            block =     {
                            'name': item.name,
                            'ip': item.ip,
                            'port': item.port,
                            'status': item.status,
                            'error': item.error,
                            'manufacturer': item.manufacturer,
                            'printer_model': item.printer_model,
                            'nozzle_diameter': item.nozzle_diameter,
                            'heated_bed': item.heated_bed,
                            'bed_temp': item.bed_temp,
                            'first_conn': str(item.first_conn),
                            'last_conn': str(item.last_conn)
                            }
            key = item.id
            pack = dict.fromkeys(str(key), block)
            printers.update(pack)
        output = json.dumps(printers)
        return output
    else:
        try:
            printer = Printer.query.filter_by(id=int(arg)).first()
            data = {'id': printer.id,
                                'name': printer.name,
                                'ip': printer.ip,
                                'port': printer.port,
                                'status': printer.status,
                                'error': printer.error,
                                'manufacturer': printer.manufacturer,
                                'printer_model': printer.printer_model,
                                'nozzle_diameter': printer.nozzle_diameter,
                                'heated_bed': printer.heated_bed,
                                'bed_temp': printer.bed_temp,
                                'first_conn': str(printer.first_conn),
                                'last_conn': str(printer.last_conn)
                                }
            return json.dumps(data)
        except:
            return jsonify(message=f'No Printer: {arg} found')


@api.route('/api/printers', methods=['PUT'])
def add_entry():
    key = request.headers['Token']
    if APIKEY.verify(key):
            data = (request.form.to_dict(flat=False))
            ip = str(data['ip']).strip("'[]")
            port = str(data['port']).strip("'[]")
            if ip == '' or port == '':
                jsonify(message='IP and Port are required'), 400
            elif len(ip) < 7:
                jsonify(message='Invalid IP address'), 400
            elif int(port)<1 or int(port)>65536:
                jsonify(message='Invalid Port'), 400
            else:
                # make new Printer entry with minimum data (IP and PORT)
                new_printer = Printer(ip, int(port), '', '', '', '', '')
                db.session.add(new_printer)
                db.session.commit()
                # update entry with the same data, this pushes the additional info like name, temp, etc
                printer = Printer.query.filter_by(id=new_printer.id).first()
                printer.upDate(str(data).strip('[]'))
                return jsonify(message="success")

    return jsonify(message='Incorrect Key')
    


'HTTP//:/api/printer?id=WhatEverIDIs&key=WhatEverTheKeyIs&U=UserName&json={}'
"http://127.0.0.1:5000/api/printers?id=2&key=f46c80b2b55d4a74a474f65c4448a2c7&u=admin&json={'status' : OK}"

@api.route('/api/printers', methods=['PATCH']) ######## doesn't work
def update_entry():
    id = request.form['Id']
    key = request.headers['Token']
    u = request.headers['User']
    data = request.form.to_dict(flat=False)
    Akey = APIKEY.query.filter_by(key=key).first()
    if Akey.verify2(u, key) == True: #### make the key something long, User can set these up, but a defult will be provided 
            try:
                printer = Printer.query.filter_by(id=id).first()
                if printer == None:
                    return jsonify(message=f"Printer: {id} was not found, are you sure that's the right ID?"), 400
                printer.upDate((str(data).strip('[]')))
                return jsonify(message='Success')
            except:
                return jsonify(message=f'An error occured while updating Printer: {id}', errors="Database_Error"), 500
    else:
        return jsonify(message=f'The key provided was invalid :('), 401
    


'HTTP//:/api/printers?id=WhatEverIDIs&key=WhatEverTheKeyIs&U=UserName'
@api.route('/api/printers', methods=['DELETE'])
def remove_entry():
    ids = request.form['Id']
    key = request.headers['Token']
    u = request.headers['User']
    Akey = APIKEY.query.filter_by(key=key).first()
    if Akey.verify2(u, key) == True: #### make the key something long, User can set these up, but a defult will be provided 
            try:
                # remove multiple printers
                if '-' in ids:
                    skip = []
                    done = []
                    start, end = ids.split('-')
                    for i in range(int(start), int(end)+1):
                        if Printer.query.filter_by(id=i).first():
                            printer = Printer.query.filter_by(id=i).first()
                            db.session.delete(printer)
                            db.session.commit()
                            done.append(i)
                        else:
                            skip.append(i)
                    if skip == []:
                        return jsonify(message=f'Printers: {ids} was removed successfully')
                    if skip !=[]:
                        return jsonify(message=f'Removed: {done}, Failed: {skip}')
                # remove one printer
                elif '-' not in ids:
                    printer = Printer.query.filter_by(id=ids).first()
                    db.session.delete(printer)
                    db.session.commit()
                    return jsonify(message=f'Printer: {ids} was removed successfully')
            except:
                return jsonify(message=f"Printer: {ids} was not found, are you sure that's the right ID?")
    elif Akey.verify2(u, key) == 'Key TIMEOUT':
        return jsonify(message=f'Key Timed out')
    else:
        return jsonify(message=f'The key provided was invalid :(')


### APIKEYS



@api.route('/APIKEYS', methods=['POST', 'GET'])
@login_required
def APIKEYS():
    if request.method == 'GET':
        return render_template('apikeys.html', user=current_user, KEYS = APIKEY, users = User)
    if request.method == 'POST':
        return redirect(url_for('api.make_key'))


@api.route('/make_key', methods=['GET', 'POST'])
@login_required
def make_key():
    if request.method == 'POST':
        userid = current_user.id
        password = request.form.get('password')
        user = User.query.filter_by(id=userid).first()
            
        if APIKEY.check_aval(userid) == False:
            flash('Users can only have 1 key at a time', category='error')
            return redirect(url_for('api.APIKEYS'))
            
        elif APIKEY.check_aval(userid) == True:
            if user.check_pass(password) == False:
                flash('Password was incorrecct', category='error')
                return render_template('makeKey.html', user=current_user)
            
            elif user.check_pass(password) == True:
                try:
                    new_key = APIKEY(userid, password)
                    db.session.add(new_key)
                    db.session.commit()
                    flash(f'Key created: {new_key.key}', category='success')
                    return redirect(url_for('api.APIKEYS'))
                except:
                    flash('There was an error while making a key', category='error')
                    return render_template('makeKey.html', user=current_user)

    if request.method == 'GET':
        return render_template('makeKey.html', user=current_user)
          




@api.route('/delete-key', methods=['POST'])
def delete_key():
    key = json.loads(request.data)
    keyid = key['keyID']
    key = APIKEY.query.get(keyid)
    if key:
        if current_user.user_type == 'admin':
            db.session.delete(key)
            db.session.commit()
            flash(f'Key: {keyid} was removed', category='success')
            return jsonify({})
        else:
            flash('Only Admins can remove Keys', category='error')