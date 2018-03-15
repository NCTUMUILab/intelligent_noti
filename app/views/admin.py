from flask import Blueprint, render_template, jsonify, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models import ContactQuestionnaire, UserQuestionnaire, User, ESMCount, DeviceID
from app import admin_only, db
from json import loads

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
        result_esm_list = []
        for entry in device_id_list:
            print("DeviceID:", entry.device_id)
            esms = ESMCount.query.filter_by(device_id=entry.device_id).all()
            for esm in esms:
                esm_name = esm.name or "None"
                for entry in result_esm_list:
                    if esm_name == entry["name"] and esm.app == entry["app"]:
                        entry["count"] += 1
                        break
                else:
                    new_entry = { "name": esm_name, "app": esm.app, "count": 1 }
                    result_esm_list.append(new_entry)
        
        contacts = ContactQuestionnaire.query.filter_by(user_id=user_id).all()
        result_facebook_list = [ contact.contact_name for contact in contacts ]
        result_line_list = [ contact.contact_name_line for contact in contacts ]
        
        return jsonify({ "esm": result_esm_list, "facebook": result_facebook_list, "line": result_line_list })
    return None
    

@admin.route('/esm/addNewContacts', methods=['POST'])
def add_new_contact():
    contact_list = loads(request.form['contacts'])
    user_id = int(request.form['userID'])
    for entry in contact_list:
        new_contact = ContactQuestionnaire(
            contact_name = entry['name'] if entry['app'] == 'facebook' else None,
            contact_name_line = entry['name'] if entry['app'] == 'line' else None,
            user_id = user_id,
            is_group = False,
            completed = False)
        db.session.add(new_contact)
    db.session.commit()
    return redirect(url_for('admin.view_esm'))


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