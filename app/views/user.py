from flask import Blueprint, render_template, redirect, url_for, flash, current_app, make_response, abort, request
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import LoginForm, RegisterForm, ForgotPassword
from app.models import User, ContactQuestionnaire, DeviceID
from app import db, on_local, load_user, admin_only

user = Blueprint('user', __name__)


@user.route('/')
def index():
    return render_template('index.html', current_user=current_user)


@user.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, self_q_completed=False, in_progress=True)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        
        new_device = DeviceID(user_id=current_user.id, device_id=form.device_id.data, is_active=False)
        db.session.add(new_device)
        db.session.commit()
        return redirect(url_for('contact.addContact'))
    return render_template('signup.html', form=form)

    
@user.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('user.dashboard'))
        return render_template('login.html', form=form, invalid_pw=True)
    return render_template('login.html', form=form, invalid_pw=False)


@user.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user.password = hashed_password
        db.session.commit()
        login_user(user)
        return redirect(url_for('user.dashboard'))
    return render_template('forgot_password.html', form=form, invalid=False)


@user.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.index'))
    

@user.route('/dashboard')
@login_required
def dashboard():
    questionnaires = ContactQuestionnaire.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', current_user=current_user, questionnaires=questionnaires)


@user.route('/change/<int:user_id>')
@admin_only
def change_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    logout_user()
    login_user(user)
    return redirect(url_for('user.dashboard'))