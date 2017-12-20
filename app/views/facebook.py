from flask import Blueprint, render_template, make_response, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import ContactQuestionnaire
from app.forms import FacebookLoginForm, FacebookResultForm
from app.get_facebook import fbMessenger, ThreadInfo
from app.testing import contacts_test
from app import db
from json import loads

facebook = Blueprint('facebook', __name__)

	
@facebook.route('/facebook/login', methods=['GET', 'POST'])
@login_required
def facebook_login():
	is_summited = ContactQuestionnaire.query.filter_by(user_id=current_user.id).first()
	if is_summited:
		return make_response(render_template('403_forbidden.html', current_user=current_user, message="You can't re-summit your facebook account!"), 403)

	form = FacebookLoginForm()
	if form.validate_on_submit():
		print("start scanning fbMessenger")
		### FACEBOOK LOGIN ###
		fb = fbMessenger(form.account.data, form.password.data)
		contacts = fb.get_messages()
		contacts = sorted(contacts, reverse=True, key=lambda c: c.msg_count)
		### TESTING ###
		# contacts = sorted(contacts_test, reverse=True, key=lambda c: c.msg_count) ## for testing
		return render_template('contact_list.html', current_user=current_user, contacts=contacts, limit=20)
	else:
		return render_template('facebook_login.html', form=form)
		

@facebook.route('/confirmContacts', methods=['POST'])
@login_required
def confirmContacts():
	contact_name_list = request.form.getlist('select')
	for name in contact_name_list:
		new_questionnaire = ContactQuestionnaire(
			contact_name=name,
			user_id=current_user.id,
			is_group=False,
			completed=False)
		db.session.add(new_questionnaire)
		db.session.commit()
	return redirect(url_for('user.dashboard'))
	

@facebook.route('/facebook/upload', methods=['GET', 'POST'])
@login_required
def uploadFacebookResult():
	form = FacebookResultForm()
	if form.validate_on_submit():
		result_str = form.file.data.read().decode('utf-8')
		result_list = sorted(loads(result_str), reverse=True, key=lambda c: c['msg_count'])
		return render_template('contact_list.html', current_user=current_user, contacts=result_list, limit=20)
	return render_template('upload_facebook_result.html', form=form)