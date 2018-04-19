from flask import Blueprint, render_template, jsonify, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models import ContactQuestionnaire, User, ESMCount, DeviceID, Notification, Result, DailyCheck
from app.helpers.daily_check import is_today_checked, Check
from app.helpers.valid_notification import valid_notification
from app import admin_only, db
from json import loads, dumps
from datetime import date, timedelta, datetime
admin = Blueprint('admin', __name__)


@admin.route('/')
@admin_only
def admin_dashboard():
    result_list = []
    users = User.query.all()
    for user in users:
        current = {}
        current['id'] = user.id
        current['name'] = user.username
        current['in_progress'] = user.in_progress
        d = DeviceID.query.filter_by(user_id=user.id).first()
        if d:
            current['device_id'] = d.device_id
        result_list.append(current)
    return render_template("admin/admin_dashboard.html", users=result_list)


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
@admin_only
def daily_check():
    print("START TO QUERY...")
    users = User.query.filter_by(in_progress=True).all()
    # today_timestamp = datetime.combine(date.today(), datetime.min.time()).timestamp() * 1000
    if request.args.get('d') == 'y':
        start_time = datetime.combine(date.today() - timedelta(1), datetime.min.time())
        end_time = datetime.combine(date.today(), datetime.min.time())
    else:
        start_time = datetime.combine(date.today(), datetime.min.time())
        end_time = datetime.now()
    print("day start: {}\nday end  : {}".format(start_time, end_time))
    check_list = [ Check(user.username, user.id, user.created_at, start_time, end_time) for user in users ]
    
    ### for each user ###
    for check in check_list:
        print("<{}>".format(check.name))
        device_entry = DeviceID.query.filter_by(user_id=check.user_id).first()
        check.device_id = device_entry.device_id
        check.esm_done_count = ESMCount.query.filter_by(device_id=check.device_id).filter(ESMCount.created_at > check.start_time).filter(ESMCount.created_at <= check.end_time).count()
        
        ### noti: im_notification_count, send_esm_count ###
        noti_day_query = Notification.query.filter_by(device_id=check.device_id).filter(Notification.timestamp > check.start_time.timestamp() * 1000).filter(Notification.timestamp <= check.end_time.timestamp() * 1000)
        check.send_esm_count = noti_day_query.filter_by(send_esm=True).count()
        for each_noti in noti_day_query.all():
            if valid_notification(each_noti.app, each_noti.ticker_text, each_noti.title, each_noti.text, each_noti.sub_text):
                check.im_notification_count += 1
        # check.im_notification_count = noti_today_query.count() - check.send_esm_count
        
        ### result: accessibility, no_result_lost ###
        day_all_result = Result.query.filter_by(user=check.device_id).filter(Result.date >= check.start_time).filter(Result.date < check.end_time).all()
        check.check_data(day_all_result)
        
        check.check_valid()
        check.fail_list = dumps(check.fail_list)
        print("\t{}, {}\n".format(check.all_valid, check.fail_list))
        # if not check.all_valid:
        #     check.warning = two_days_fail(check.user_id)
        
    return render_template("admin/daily.html", users=check_list, is_today_checked=is_today_checked(), check_json=[ c.__dict__ for c in check_list ])


@admin.route('/daily/post', methods=['POST'])
@admin_only
def daily_check_post():
    data_list = loads(request.form['check'])
    for check in data_list:
        new_check = DailyCheck(
            user_id = check['user_id'],
            date = datetime.now().today(),
            send_esm_count = check['send_esm_count'],
            esm_done_count = check['esm_done_count'],
            accessibility = check['accessibility'],
            no_result_lost = check['no_result_lost'],
            im_notification_count = check['im_notification_count'],
            all_valid = check['all_valid'],
            fail_list = check['fail_list'])
        db.session.add(new_check)
    db.session.commit()
    return "checked!"