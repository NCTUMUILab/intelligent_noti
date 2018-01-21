from flask import Blueprint, render_template, redirect, url_for, request, make_response
from flask_login import login_required, current_user
from app.models import ContactQuestionnaire, UserQuestionnaire
from app.helpers import find_questionnaire
from app import db
from json import dumps, loads, load
from functools import wraps

questionnaire = Blueprint('questionnaire', __name__)


def check_questionnaire(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        questionnaire_id = kwargs['questionnaire_id']
        questionnaires = ContactQuestionnaire.query.filter_by(user_id=current_user.id).all()
        for questionnaire in questionnaires:
            if questionnaire_id == questionnaire.id:
                return f(questionnaire_id, questionnaire)
        else:
            return make_response(render_template('403_forbidden.html', current_user=current_user, message="Invalid Qestionnaire Access"), 403)
    return decorated_function


@questionnaire.route('/questionnaire/<int:questionnaire_id>', methods=['GET', 'POST'])
@login_required
@check_questionnaire
def contact_questionnaire(questionnaire_id, questionnaire):
    if request.method == 'GET':
        last_result = loads(questionnaire.data) if questionnaire.data else None
        question_list = load(open("app/questionnaire/contact_questionnaire.json"))
        return render_template('contact_questionnaire.html', questionnaire=questionnaire, last_result=last_result, question_list=question_list)
    
    elif request.method == 'POST':
        answers_dict = request.form.to_dict(flat=True)
        questionnaire.data = dumps(answers_dict, ensure_ascii=False)
        questionnaire.completed = True
        db.session.commit()
        return redirect(url_for('user.dashboard'))


@questionnaire.route('/questionnaire/user', methods=['GET', 'POST'])
@login_required
def user_questionnaire():
    userQ = UserQuestionnaire.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'GET':
        last_result = loads(userQ.data) if userQ else None
        question_list = load(open("app/questionnaire/user_questionnaire.json"))
        return render_template('user_questionnaire.html', last_result=last_result, question_list=question_list)

    elif request.method == 'POST':
        answers_dict = request.form.to_dict(flat=True)
        if not userQ: # new questionnaire
            new_user_q = UserQuestionnaire(
                user_id = current_user.id,
                completed = True,
                data = dumps(answers_dict, ensure_ascii=False))
            db.session.add(new_user_q)
            db.session.commit()
        else: # modify questionnaire
            userQ.data = dumps(answers_dict, ensure_ascii=False)
            db.session.commit()
        return redirect(url_for('user.dashboard'))