from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import User # SQL models
from . import db # import db from __init__
import time



auth = Blueprint('auth', __name__)


from . import create_admin, config


@auth.route('/login', methods=['GET', 'POST', 'PUT'])
def login():
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if user.check_pass(password):
                    login_user(user, remember=True)
                    flash(f'Logged in successfully! Welcome {user.name}', category='success')
                    user.upDate()
                    db.session.commit()
                    return redirect(url_for('views.home'))
            else:
                flash("Incorrect password, try again.", category='error')
                
        else:
            flash("Email does not exist.", category='error')
    if request.method == 'PUT':
        create_admin()
        flash("ADMIN ACCOOUNT SETUP", category='success')
        return render_template("login.html", user=current_user, add=False)
    if User.query.filter_by(email=config('boot', 'admin_eml')).first() == None:
        return render_template("login.html", user=current_user, add=config('boot', 'admin_acc'))
    
    elif User.query.filter_by(email=config('boot', 'admin_eml')).first():
        return render_template("login.html", user=current_user, add=False)
        

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(email=email).first() #check if accout exists
        if user:
            flash("Email already exists.", category='error')
            return redirect(url_for('auth.login'))

        # check signup requirements 
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", category='error')
        elif len(firstname) < 2:
            flash("First name must be greater than 1 character.", category='error')
        elif len(lastname) <2:
            flash("Last name is required for signup.", category='error')
        elif password1 != password2:
            flash("Passwords don\'t match", category='error')
        elif len(password1) <7:
            flash("Password must be at least 7 characters.", category='error')
        # push new client data 
        else:
            new_user = User(firstname, lastname, email, 'Standard', password1)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for("views.home"))
    return render_template("sign_up.html", user=current_user)
