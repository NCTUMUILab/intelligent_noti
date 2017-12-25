from flask import Blueprint, render_template, make_response, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import ContactQuestionnaire
from app.forms import FacebookLoginForm, FacebookResultForm
from app.get_facebook import fbMessenger, ThreadInfo
from app.testing import contacts_test
from app.helpers import find_questionnaire
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
	is_summited = ContactQuestionnaire.query.filter_by(user_id=current_user.id).first()
	if is_summited:
		return make_response(render_template('403_forbidden.html', current_user=current_user, message="You can't re-summit your facebook account!"), 403)
		
	contact_name_list = request.form.getlist('select')
	for name in contact_name_list:
		facebook_name = name.split('||')[0] if '||' in name else name
		line_name     = name.split('||')[1] if '||' in name else ""

		new_questionnaire = ContactQuestionnaire(
			contact_name=facebook_name,
			contact_name_line=line_name,
			user_id=current_user.id,
			is_group=False,
			completed=False)
		db.session.add(new_questionnaire)
		db.session.commit()
	return redirect(url_for('user.dashboard'))
	

@facebook.route('/facebook/upload', methods=['GET', 'POST'])
@login_required
def uploadFacebookResult():
	is_summited = ContactQuestionnaire.query.filter_by(user_id=current_user.id).first()
	if is_summited:
		return make_response(render_template('403_forbidden.html', current_user=current_user, message="You can't re-summit your facebook account!"), 403)
	
	form = FacebookResultForm()
	if form.validate_on_submit():
		result_facebook_str = form.file_facebook.data.read().decode('utf-8')
		result_list = loads(result_facebook_str)
		if form.file_line.data:
			result_line_str = form.file_line.data.read().decode('utf-8')
			result_list.extend(loads(result_line_str))
			
		result_list = sorted(result_list, reverse=True, key=lambda c: c['msg_count'])
		return render_template(
			'contact_list.html', 
			current_user=current_user, 
			contacts=result_list, 
			limit=20,
			pre_selected=20)
		
	return render_template('upload_result.html', form=form)


@facebook.route('/facebook/editName/<int:user_id>/<int:questionnaire_id>', methods=['POST'])
@login_required
def editName(user_id, questionnaire_id):
	error, message, questionnaire = find_questionnaire(current_user=current_user, user_id=user_id, questionnaire_id=questionnaire_id)
	if error:
		return message
	
	if request.method == 'POST':
		contact = ContactQuestionnaire.query.filter_by(id=questionnaire_id).first()
		if request.form['appNewName'] == "facebook":
			contact.contact_name = request.form['name']
		elif request.form['appNewName'] == "line":
			contact.contact_name_line = request.form['name']
		db.session.commit()
		return redirect(url_for('user.dashboard'))