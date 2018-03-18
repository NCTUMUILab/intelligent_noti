from flask import Blueprint, render_template, jsonify, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models import ContactQuestionnaire, User, ESMCount, DeviceID, Notification
from app import admin_only, db
from json import loads
from datetime import datetime

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
        for device_id_user in device_id_list:
            print("DeviceID:", device_id_user.device_id)
            esms = ESMCount.query.filter_by(device_id=device_id_user.device_id).all()
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
        print("entry['app']:", entry['app'])
        new_contact = ContactQuestionnaire(
            contact_name = entry['name'] if entry['app'] == 'facebook' else None,
            contact_name_line = entry['name'] if entry['app'] == 'line' else None,
            user_id = user_id,
            is_group = False,
            completed = False)
        db.session.add(new_contact)
    db.session.commit()
    return redirect(url_for('admin.view_esm'))

@admin.route('/daily')
def daily_check():
    users = User.query.filter_by(in_progress=True).all()
    user_list = [ {
        'name': user.username, 
        'id': user.id, 
        'day': (datetime.now()-user.created_at).days+1, 
        'esm': 0,
        'noti': 0 } for user in users ]
    
    all_devices = DeviceID.query.all()
    for user in user_list:
        for device in all_devices:
            if device.user_id == user['id']:
                user['device_id'] = device.device_id
                break
        for esm in ESMCount.query.filter_by(device_id=user['device_id']).all():
            if esm.created_at.date() == datetime.now().date():
                user['esm'] += 1
        
        # for noti in Notification.query.filter_by(device_id=user['device_id']).all():
        #     if noti.
        
    return render_template("admin/daily.html", users=user_list)