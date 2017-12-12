from flask import render_template, redirect, url_for, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from json import dumps
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import uuid
from flask_cors import CORS, cross_origin
import dateutil.parser
from sqlalchemy import desc
import hashlib

from . import app, db, load_user, admin_only
from .models import *
from .forms import LoginForm, RegisterForm, FacebookLoginForm
from .get_facebook import fbMessenger, ThreadInfo
from .testing import contacts_test
import csv


### route ###
@app.route('/')
def index():
	return render_template('index.html', current_user=current_user)

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
# @admin_only
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
	userQ_done = UserQuestionnaire.query.filter_by(user_id=current_user.id).first()
	return render_template('dashboard.html', current_user=current_user, questionnaires=questionnaires, userQ_done=userQ_done)

### Facebook ###
@app.route('/facebook', methods=['GET', 'POST'])
@login_required
def facebook():
	is_summited = ContactQuestionnaire.query.filter_by(user_id=current_user.id).first()
	if is_summited:
		return make_response(render_template('403_forbidden.html', current_user=current_user, message="You can't re-summit your facebook account!"), 403)

	form = FacebookLoginForm()
	if form.validate_on_submit():
		print("start scanning fbMessenger")
		# facebook login
		fb = fbMessenger(form.account.data, form.password.data)
		contacts = fb.get_messages()
		contacts = sorted(contacts, reverse=True, key=lambda c: c.msg_count)
		# for testing
		# contacts = sorted(contacts_test, reverse=True, key=lambda c: c.msg_count) ## for testing
		return render_template('contact_list.html', name=current_user.username, contacts=contacts, limit=4)

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

@app.route('/questionnaire/<int:user_id>/<int:questionnaire_id>', methods=['GET', 'POST'])
@login_required
def questionnaire(user_id, questionnaire_id):
	error, message, questionnaire = find_questionnaire(current_user=current_user, user_id=user_id, questionnaire_id=questionnaire_id)
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
		return make_response(render_template('403_forbidden.html', current_user=current_user, message="You have done the user questionnaire!"), 403)

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

@app.route('/heatmap', methods=['GET', 'POST'])
@login_required
def heatmap():
	return render_template('heatmap.html')

@app.route('/getLocations', methods=['POST'])
def getLocations():
	marks = []
	f = open('result.csv', 'r')
	for row in csv.DictReader(f):
		loc = (row['raw'].split('\t')[2], row['raw'].split('\t')[3])
		marks.append(loc)
		print(row['raw'].split('\t')[2])
	f.close()
	locations = {"marks": marks}
	return jsonify(locations)


@app.route('/form/', methods=['POST'])
def add_form():
    content = request.get_json(silent=True)
    r = FormResult({'raw': str(content), 'wid': content['wid'], 'user': content['user'], 'hash': content['hash'], 'sender': content['title'], 'app': content['app']})
    db.session.add(r)
    try:
        db.session.commit()
        msg = 'ok'
    except Exception as e:
         print(e)
         db.session.rollback()
         msg = 'error'
    return jsonify({'msg': msg})


@app.route('/upload/', methods=['POST'])
def add_result():
    content = request.get_json(silent=True)
    print('len: ', len(content))
    print('first id:', content[0]['id'])
    for c in content:
        result = Result(c)
        db.session.add(result)
        try:
            db.session.commit()
            msg = 'ok'
        except Exception as e:
            print(e)
            db.session.rollback()
            msg = 'error'
    if content:
        user = content[0]['user']
    result = db.session.query(FormResult).filter(FormResult.user).order_by(desc(FormResult.created_at)).first()
    if result:
        result = result.created_at
    print({'msg': 'ok', 'last_form': result})
    return jsonify({'msg': 'ok', 'last_form': result})

@app.route('/notification/')
def get_notification():
    delta = datetime.utcnow() - timedelta(minutes=600)
    user = request.args.get('user')
    u = db.session.query(User).filter(User.phone_id==user).one_or_none()
    notification = db.session.query(Result).filter(Result.r_type == 'Notification').filter(Result.user == user).filter(Result.date > delta).order_by(desc(Result.created_at)).all()
    db.session.close()
    notifications = []
    wids = []
    for n in notification:
        noti = n.raw.split('\t')
        p = {}
        if noti[0] == 'com.facebook.orca':
            p['app'] = 'Facebook'
            p['title'] = noti[1]
            p['content'] = noti[2]
            p['time'] = n.date
            p['white_list_user'] = db.session.query(ContactQuestionnaire).filter(ContactQuestionnaire.user_id==u.id).filter(ContactQuestionnaire.contact_name==p['title']).one_or_none()

            if not p['white_list_user']:
                continue
            wids.append(p['white_list_user'].id)
            p['wid'] = p['white_list_user'].id
            p['hash'] = hashlib.md5((str(noti[0:2]) + str(n.date)).encode()).hexdigest()
            p['done'] = bool(db.session.query(FormResult).filter(FormResult.hash==p['hash']).one_or_none())
            notifications.append(p)
    notifications = sorted(notifications, key=lambda k: k['time'])
    wid_count = {}
    for wid in wids:
        wid_count[wid] = db.session.query(FormResult).filter(FormResult.wid==wid).count()
    _wid_count = wid_count
    wid_count = sorted(wid_count, key=wid_count.get)
    selected = []
    for w in wid_count[0:3]:
        for n in notifications:
            if n['wid'] == w:
                selected.append(n)
                break
    return render_template('notification.html', notification=selected, wid_count=_wid_count)
