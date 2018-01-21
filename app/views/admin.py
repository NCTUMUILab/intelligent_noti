from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import ContactQuestionnaire, UserQuestionnaire, User
from app import admin_only

admin = Blueprint('admin', __name__)

@admin.route('/esm')
@admin_only
def view_esm():
    return "still working on that"

@admin.route('/questionnaire')
@admin_only
def view_questionnaire():
    users = User.query.all()
    questionniares = ContactQuestionnaire.query.all()
    
    q_num, q_completed = {}, {}
    for q in questionniares:
        q_num[q.user_id] = q_num.get(q.user_id, 0) + 1
        if q.completed:
            q_completed[q.user_id] = q_completed.get(q.user_id, 0) + 1
    
    user_Qs = UserQuestionnaire.query.all()
    user_Q_completed = []
    for user_Q in user_Qs:
        user_Q_completed.append(user_Q.user_id)
    
    print(user_Q_completed)
    
    return render_template("admin/questionnaire.html", users=users, q_num=q_num, q_completed=q_completed, user_Q_completed=user_Q_completed)