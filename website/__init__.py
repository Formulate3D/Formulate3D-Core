from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from sqlalchemy_json import mutable_json_type
from flask_modals import Modal
from flask_compress import Compress ## text compression
import json
import os
#from flask_socketio import SocketIO


### imports for main
import sys
import shutil
###imports for main

def center(string):
    print(string.center(shutil.get_terminal_size().columns))

def config(domain, val):
    f = open('website/config.config', 'r')
    data = json.load(f)
    data = data[domain]
    for key, value in data.items():
        if key == val:
            return value
    
def Configcheck():
    if os.path.exists('website/config.config'):
        return True
    else:
        center("### NO CONFIG FILE FOUND ###")
        print("With no config file, defaults will be used.")
        input("Press Enter to continue: ")
        return False

    #print(config('boot', 'admin_acc'))




def checkvers():
    center(f'Python version: {sys.version}')


    if '3.6' not in sys.version:
        center('''\n
       ### IMPORTANT ###
       This application was built on Python 3.6.4, stability is not garenteed on this version of python
       ### IMPORTANT ###
        \n''')


def checks():
    checkvers()
    Configcheck()

db = SQLAlchemy()
DB_NAME = "database.db"

modal = Modal()


compress = Compress()


#socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)
    modal.init_app(app)
    app.config["COMPRESS_ALGORITHM"] = 'br'  # disable default compression of all eligible requests
    compress.init_app(app)
    #socketio.init_app(app)
    


    from .views import views
    from .auth import auth
    from .api import api

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(api, url_prefix='/')

    from .models import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id)) # tells Flask how to load the user

    
    return app

def create_database(app):
    if not path.exists('website/' + str(DB_NAME)):
        db.create_all(app=app)
        print("----- DATABASE CREATED -----")

def create_admin():
    if config('boot', 'admin_acc'):
        from .models import User
        if User.query.filter_by(email=config('boot', 'admin_eml')).first():
            print("----- ADMIN ACCOUNT PRESENT -----")
        else:
            admin_acc = User('admin', 'admin', config('boot', 'admin_eml'), 'admin', config('boot', 'admin_pas'))
            db.session.add(admin_acc)
            db.session.commit()
            print("----- ADMIN ACCOUNT CREATED -----")










