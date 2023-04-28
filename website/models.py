from . import db, config
from flask_login import UserMixin
from sqlalchemy.sql import func

import uuid

from datetime import datetime, timedelta
import time

import ast

### moved hasjhing from auth to models to make calls for checks easier
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


ph = PasswordHasher()

def timeNOW():
    return datetime.now()

###import sqlalchemy-String 0.5.0

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    lname = db.Column(db.String(256))
    email = db.Column(db.String(256), unique=True)
    user_type = db.Column(db.String(10))
    password = db.Column(db.String(512))
    number_prints = db.Column(db.Integer)
    setup_time = db.Column(db.DateTime(timezone=True), default=timeNOW()) ### auto sets time
    last_conn_time = db.Column(db.DateTime)   ### needs to be updated 
    groups = db.Column(db.String) ### using muteableString module
    elevate = db.Column(db.String)

    def __init__(self, name, lname, email, user_type, password): ### only called when new user is created; this does a qick setup of the default data
        self.name = name
        self.lname = lname
        self.email = email
        self.user_type = user_type
        self.password = ph.hash(password)
        self.number_prints = 0
        self.last_conn_time = timeNOW()

    def check_pass(self, password):
        try:
            if ph.verify(self.password, password):
                return True
        except VerifyMismatchError:
            return False
    def upDate(self):
        self.last_conn_time = timeNOW()


    
class Printer(db.Model):
    ### main printer information
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    ip = db.Column(db.String(16))
    port = db.Column(db.Integer)
    status = db.Column(db.String(128))
    error = db.Column(db.String) ### errors should only be read if the status is set to "error"
    key = db.Column(db.String)

    ### printer information
    manufacturer = db.Column(db.String(128))
    printer_model = db.Column(db.String(128))
    nozzle_diameter = db.Column(db.Float)
    ### heated bed infomation
    heated_bed = db.Column(db.Boolean)
    bed_temp = db.Column(db.Float) ### bed temp is disregarded if heated_bed == 0 (flase)

    ### conn times
    first_conn = db.Column(db.DateTime(timezone=True), default=timeNOW())
    last_conn = db.Column(db.DateTime)

    def __init__(self, ip, port, name, manufacturer, printer_model, nozzle_diameter, heated_bed): ### only called when new printer is created; this does a qick setup of the default data
        self.ip = ip
        self.port = port
        self.last_conn = timeNOW()
        if name == '':
            self.name = "NA"
        else:
            self.name = name
        if manufacturer == '':
            self.manufacturer='NA'
        else:
            self.manufacturer=manufacturer
        if printer_model == '':
            self.printer_model='NA'
        else:
            self.printer_model=printer_model
        if nozzle_diameter == '':
            self.nozzle_diameter=0.0
        else:
            self.nozzle_diameter=nozzle_diameter
        if heated_bed == '':
            self.heated_bed = False
        else:
            self.heated_bed = heated_bed

    def load(self):
        data = {'id': self.id}

    # takes in a str dict and updates any key values to their associated value
    def upDate(self, data):
            try:
                data = ast.literal_eval(data)
            except:
                return False
            for key, value in data.items():
                if key != 'id':
                    if key in self.__dict__:
                        try:
                            setattr(self, key, str(value).strip("'[]"))
                            db.session.commit()
                            self.load() #### data needs to be loaded or it doesn't commit properly???? without doing this, not a single update actually commits....   print(self.{AnyItem}) also solves this issue, but I use the load function so nothing is output to terminal
                        except Exception as e:
                            print("Error during DB update", e)
            return True

class Print_History(db.Model):
    ### IDs
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    printer_id = db.Column(db.Integer, db.ForeignKey("printer.id"))

    ### times
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    total_time = db.Column(db.Time)
    ### other information
    error = db.Column(db.String) ### can be empty / only used if erros occur



class APIKEY(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    key = db.Column(db.String(80))
    time = db.Column(db.DateTime)

    def __init__(self, user_id, passw):
        self.user_id = user_id
        user = User.query.filter_by(id = user_id).first()
        if user.check_pass(passw):
            self.key = uuid.uuid4().hex
            #print(self.key)
        self.time = timeNOW()

    def updatekey(self):
        newkey = uuid.uuid4().hex
        if newkey != self.key:
            self.key = newkey
            self.time = timeNOW()
            db.session.commit()


    # checks Key creation time against its live time -- returns remaining time if any, else returns "INVALID"
    def timeval(self):
        if config("API", "key_time") == False:
            return "None"
        # Time manipluation is hard okay.... I'm trying my best
        timeS = self.time # get key creation time
        unixi = time.mktime(timeS.timetuple()) # convert to unix time
        unixf = time.mktime((datetime.strptime(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S')).timetuple()) # get current time in unix
        delta = unixf - unixi # make a time delta with both unix vlaues
        #print(delta)
        Ftime = timedelta(seconds=delta) # makes it a timedelta object
        Rtime = timedelta(days=int(config("API", "key_time"))) - Ftime # convert timedelta to number of days (pushes into negatives)
        if int(Rtime.days) < 0: #check if time remaining < 0
            return 'INVALID' # could just return False, but I can use this to easily respond to API calls by giving this function as the return
        else:
            return Rtime # retuns remaining time

    def verify(key):
        if APIKEY.query.filter_by(key=key).first():
            if APIKEY.query.filter_by(key=key).first().timeval() != 'INVALID':
                return True
            else:
                return 'Key TIMEOUT'


    def verify2(self, user, key):
        if self.timeval() != 'INVALID':
            userc = User.query.filter_by(name=user).first()
            if self.user_id == userc.id:
                if key == self.key:
                    return True
                else:
                    return 'Incorect key'
            else:
                return 'Invalid User'
        else:
            return 'Key TIMEOUT'

    
        
    def check_aval(userid):
        for entry in APIKEY.query.all():
            if entry.user_id == userid:
                return False ### if a key already exists for account
        return True ### if there are no keys from the user