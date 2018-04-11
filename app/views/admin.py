from flask import Blueprint, render_template, jsonify, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models import ContactQuestionnaire, User, ESMCount, DeviceID, Notification, Result, DailyCheck
from app import admin_only, db
from json import loads
from datetime import date, timedelta, datetime
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


def check_valid(check, latest_result_raw):
    fail_reason_list = []
    record_valid = True
    if check['im_notification_count'] <= 10:
        record_valid = False
        fail_reason_list.append('im_notification_count')
    if check['send_esm_count'] <= 5:
        record_valid = False
        fail_reason_list.append('send_esm_count')
    if check['esm_done_count'] <= 2:
        record_valid = False
        fail_reason_list.append('esm_done_count')
    if latest_result_raw or True:
        pass
    return record_valid, fail_reason_list


def is_today_checked():
    last_check = DailyCheck.query.order_by(DailyCheck.created_at.desc()).first()
    if last_check and last_check.created_at.date() == datetime.now().date():
        return True
    return False


def is_consecutive_invalid(user_id):
    last_check = DailyCheck.query.filter_by(user_id=user_id).order_by(DailyCheck.created_at.desc()).first()
    if last_check and not last_check.all_valid:
        return True
    return False


@admin.route('/daily')
@admin_only
def daily_check():
    users = User.query.filter_by(in_progress=True).all()
    today_timestamp = datetime.combine(date.today(), datetime.min.time()).timestamp() * 1000
    
    check_list = [ {
        'name': user.username, 
        'user_id': user.id, 
        'device_id': '',
        'day': (datetime.now()-user.created_at).days+1, 
        'send_esm_count': 0,
        'esm_done_count': 0,
        'im_notification_count': 0,
        'phone_data_count': 0,
        'all_valid': True,
        'warning': False } for user in users ]
    
    ### for each user ###
    for check in check_list:
        device_entry = DeviceID.query.filter_by(user_id=check['user_id']).first()
        check['device_id'] = device_entry.device_id
        check['esm_done_count'] = ESMCount.query.filter_by(device_id=check['device_id']).filter(ESMCount.created_at > date.today()).count()
        noti_today_query = Notification.query.filter_by(device_id=check['device_id']).filter(Notification.timestamp > today_timestamp)
        check['send_esm_count'] = noti_today_query.filter_by(send_esm=True).count()
        check['im_notification_count'] = noti_today_query.count()
        check['phone_data_count'] = Result.query.filter_by(user=check['device_id']).filter(Result.date > date.today()).count()
        latest_result = Result.query.filter_by(user=check['device_id']).order_by(Result.date.desc()).first()
        
        check['all_valid'], fail_reason_list = check_valid(check, latest_result.raw if latest_result else None)
        print("{}: {}, {}".format(check['name'], check['all_valid'], fail_reason_list))
        if not check['all_valid']:
            check['warning'] = is_consecutive_invalid(check['user_id'])
        

    return render_template("admin/daily.html", users=check_list, is_today_checked=is_today_checked())


@admin.route('/daily/post', methods=['POST'])
@admin_only
def daily_check_post():
    check_result_list = loads(request.form['check'])
    for check in check_result_list:
        new_check = DailyCheck(
            user_id = check['user_id'],
            date = datetime.now().today(),
            send_esm_count = check['send_esm_count'],
            esm_done_count = check['esm_done_count'],
            im_notification_count = check['im_notification_count'],
            phone_data_count = check['phone_data_count'],
            all_valid = check['all_valid'])
        db.session.add(new_check)
    db.session.commit()
    return redirect(url_for('admin.daily_check'))