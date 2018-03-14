from flask import Blueprint, render_template, jsonify, request, jsonify
from flask_login import login_required, current_user
from app.models import ContactQuestionnaire, UserQuestionnaire, User, ESMCount, DeviceID
from app import admin_only

admin = Blueprint('admin', __name__)


@admin.route('/esm')
@admin_only
def view_esm():
    users = User.query.all()
    esms = ESMCount.query.all()
    return render_template("admin/esm.html", esms=esms, users=users)


@admin.route('/esm/get')
def get_esm():
    user_id = request.args.get('uid');
    if user_id:
        device_id_list = DeviceID.query.filter_by(user_id=user_id).all()
        result_dict = {}
        for entry in device_id_list:
            print("DeviceID:", entry.device_id)
            esms = ESMCount.query.filter_by(device_id=entry.device_id).all()
            for esm in esms:
                if esm.name in result_dict:
                    result_dict[esm.name] += 1
                else:
                    result_dict[esm.name] = 1
        if None in result_dict:
            result_dict['None'] = result_dict.pop(None)
        return jsonify(result_dict)
    return None
    

@admin.route('/esm/addNewContact')
def add_new_contact():
    new_contact_name = request.args.get('contact')
    user_name = request.args.get('user')
    return "success"


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
    
    return render_template("admin/questionnaire.html", users=users, q_num=q_num, q_completed=q_completed, user_Q_completed=user_Q_completed)