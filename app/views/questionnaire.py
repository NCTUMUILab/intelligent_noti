from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import ContactQuestionnaire, UserQuestionnaire
from app import db
from json import dumps, loads

questionnaire = Blueprint('questionnaire', __name__)

def find_questionnaire(current_user, user_id, questionnaire_id):
	if user_id != current_user.id:
		return 1, "you are not this user!", None

	questionnaires = ContactQuestionnaire.query.filter_by(user_id=current_user.id).all()
	for questionnaire in questionnaires:
		if questionnaire_id == questionnaire.id:
			return 0, "Found", questionnaire
	return 2, "you don't have THIS questionnaire", None
	

@questionnaire.route('/questionnaire/<int:user_id>/<int:questionnaire_id>', methods=['GET', 'POST'])
@login_required
def contact_questionnaire(user_id, questionnaire_id):
	error, message, questionnaire = find_questionnaire(current_user=current_user, user_id=user_id, questionnaire_id=questionnaire_id)
	if error:
		return message

	if request.method == 'POST':
		answers_dict = request.form.to_dict(flat=True)
		questionnaire.data = dumps(answers_dict, ensure_ascii=False)
		questionnaire.completed = True
		db.session.commit()
		return redirect(url_for('user.dashboard'))

	elif request.method == 'GET':
		return render_template('contact_questionnaire.html', questionnaire=questionnaire)


@questionnaire.route('/user_questionnaire', methods=['GET', 'POST'])
@login_required
def user_questionnaire():
	userQ = UserQuestionnaire.query.filter_by(user_id=current_user.id).first()
	
	if request.method == 'GET':
		userQ = loads(userQ.data) if userQ else None
		return render_template('user_questionnaire.html', userQ=userQ)

	elif request.method == 'POST':
		answers_dict = request.form.to_dict(flat=True)
		if not userQ:
			new_user_q = UserQuestionnaire(
				user_id=current_user.id,
				completed=True,
				data=dumps(answers_dict, ensure_ascii=False))
			db.session.add(new_user_q)
		else:
			userQ.data=dumps(answers_dict, ensure_ascii=False)
		db.session.commit()
		return redirect(url_for('user.dashboard'))