from flask import render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from models import app, db, User, ContactQuestionnaire, UserQuestionnaire
from forms import LoginForm, RegisterForm, FacebookLoginForm
from login import login_manager, load_user
from get_facebook import fbMessenger, ThreadInfo
from json import dumps
from testing import contacts_test


# init bootstrap
Bootstrap(app)

### route ###
@app.route('/')
def index():
	return render_template('index.html')

## User System ##
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('dashboard'))
		else:
			return 'Invalid username or password'
	return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegisterForm()
	
	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data, method='sha256')
		new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(new_user)
		db.session.commit()
		login_user(new_user)
		return redirect(url_for('facebook'))
	
	return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

### Main page
@app.route('/dashboard')
@login_required
def dashboard():
	questionnaires = ContactQuestionnaire.query.filter_by(user_id=current_user.id).all()
	return render_template('dashboard.html', name=current_user.username, questionnaires=questionnaires)

### Facebook ###
@app.route('/facebook', methods=['GET', 'POST'])
@login_required
def facebook():
	form = FacebookLoginForm()
	if form.validate_on_submit():
		print("start scanning fbMessenger")
		# fb = fbMessenger(form.account.data, form.password.data)
		# contacts = fb.get_messages()
		# contacts = sorted(contacts, reverse=True, key=lambda c: c.msg_count)
		contacts = sorted(contacts_test, reverse=True, key=lambda c: c.msg_count) ## for testing
		return render_template('contact_list.html', name=current_user.username, contacts=contacts)
	
	return render_template('facebook_login.html', form=form)

@app.route('/confirmContacts', methods=['POST'])
@login_required
def confirmContacts():
	contact_name_list = request.form.getlist('select')
	for name in contact_name_list:
		is_group = request.form['{}_is_group'.format(name)] == 'True'
		new_questionnaire = ContactQuestionnaire(
			contact_name=name, 
			user_id=current_user.id, 
			is_group=is_group, 
			completed=False)
		db.session.add(new_questionnaire)
		db.session.commit()
	return redirect(url_for('dashboard'))

### Questionnare System ###
def find_questionnaire(current_user, user_id, questionnaire_id):
	if user_id != current_user.id:
		return 1, "you are not this user!", None
	
	questionnaires = ContactQuestionnaire.query.filter_by(user_id=current_user.id).all()
	for questionnaire in questionnaires:
		if questionnaire_id == questionnaire.id:
			return 0, "Found", questionnaire
	return 2, "you don't have THIS questionnaire", None

@app.route('/questionnaire/<user_id>/<questionnaire_id>', methods=['GET', 'POST'])
@login_required
def questionnaire(user_id, questionnaire_id):
	error, message, questionnaire = find_questionnaire(current_user=current_user, user_id=int(user_id), questionnaire_id=int(questionnaire_id))
	if error:
		return message
	
	if request.method == 'POST':
		answers_dict = request.form.to_dict(flat=True)
		questionnaire.data = dumps(answers_dict, ensure_ascii=False)
		questionnaire.completed = True
		db.session.commit()
		return redirect(url_for('dashboard'))
	
	elif request.method == 'GET':
		if questionnaire.is_group:
			return render_template('group_questionnaire.html', questionnaire=questionnaire)
		else:
			return render_template('contact_questionnaire.html', questionnaire=questionnaire)

@app.route('/user_questionnaire', methods=['GET', 'POST'])
@login_required
def user_questionnaire():
	questionnaire_done = UserQuestionnaire.query.filter_by(user_id=current_user.id).first()
	if questionnaire_done:
		return "you have done the user questionnaire!"
	
	if request.method == 'GET':
		return render_template('user_questionnaire.html')
	
	elif request.method == 'POST':
		answers_dict = request.form.to_dict(flat=True)
		new_user_q = UserQuestionnaire(
			user_id=current_user.id, 
			completed=True, 
			data=dumps(answers_dict, ensure_ascii=False))
		db.session.add(new_user_q)
		db.session.commit()
		return redirect(url_for('dashboard'))
		
		

if __name__ == '__main__':
	app.run(debug=True)