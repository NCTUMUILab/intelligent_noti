from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import LoginForm, RegisterForm
from app.models import User, ContactQuestionnaire, UserQuestionnaire
from app import db, admin_only, load_user

user = Blueprint('user', __name__)


@user.route('/')
def index():
	return render_template('index.html', current_user=current_user)


@user.route('/signup', methods=['GET', 'POST'])
# @admin_only
def signup():
	form = RegisterForm()
	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data, method='sha256')
		new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(new_user)
		db.session.commit()
		login_user(new_user)
		return redirect(url_for('contact.addContact'))
	return render_template('signup.html', form=form)

	
@user.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('user.dashboard'))
		else:
			return 'Invalid username or password'
	return render_template('login.html', form=form)


@user.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('user.index'))
	

@user.route('/dashboard')
@login_required
def dashboard():
	questionnaires = ContactQuestionnaire.query.filter_by(user_id=current_user.id).all()
	userQ_done = UserQuestionnaire.query.filter_by(user_id=current_user.id).first()
	return render_template('dashboard.html', current_user=current_user, questionnaires=questionnaires, userQ_done=userQ_done)