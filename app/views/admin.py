from flask import Blueprint, render_template, jsonify, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.models import ContactQuestionnaire, User, ESMCount, DeviceID, Notification, Result, DailyCheck, APPState
from app.helpers.daily_check import Check
from app.helpers.valid_notification import valid_notification
from app import admin_only, db
from json import loads, dumps
from datetime import date, timedelta, datetime
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
admin = Blueprint('admin', __name__)

def mean(l):
    return sum(l) / len(l)

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
        s = APPState.query.filter_by(device_id=d.device_id).order_by(APPState.created_at.desc()).first()
        if s:
            current['state'] = [
                {
                    'key': 'accessibility',
                    'date': s.state_accessibility,
                    'label': '1hr',
                    'alert': (datetime.now() - s.state_accessibility) > timedelta(hours=1)
                },
                {
                    'key': 'stream',
                    'date': s.state_stream,
                    'label': '1hr',
                    'alert': (datetime.now() - s.state_stream) > timedelta(hours=1)
                },
                {
                    'key': 'notification_listen',
                    'date': s.state_notification_listen,
                    'label': '1hr',
                    'alert': (datetime.now() - s.state_notification_listen) > timedelta(hours=1)
                },
                {
                    'key': 'notification_sent_esm',
                    'date': s.state_notification_sent_esm,
                    'label': '12hr',
                    'alert': (datetime.now() - s.state_notification_sent_esm) > timedelta(hours=12)
                },
                {
                    'key': 'esm_done',
                    'date': s.state_esm_done,
                    'label': '24hr',
                    'alert': (datetime.now() - s.state_esm_done) > timedelta(hours=24)
                },
                {
                    'key': 'wifi_upload',
                    'date': s.state_wifi_upload,
                    'label': '24hr',
                    'alert': (datetime.now() - s.state_wifi_upload) > timedelta(hours=24)
                }
            ]

        result_list.append(current)

    all_esm_done_mean = mean([ i.esm_done_count for i in DailyCheck.query.all() ])
    week_esm_done_mean = mean([ i.esm_done_count for i in DailyCheck.query.filter(DailyCheck.date >= date.today() - timedelta(7)).all() ])
    return render_template("admin/admin_dashboard.html", users=result_list, all_mean=all_esm_done_mean, week_mean=week_esm_done_mean)


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
def daily_check_get():
    yesterday_record = request.args.get('d') == 'y'
    if yesterday_record:
        start_time = datetime.combine(date.today() - timedelta(1), datetime.min.time())
    else:
        start_time = datetime.combine(date.today(), datetime.min.time())
    print("DAY START: {}\n".format(start_time))

    users = User.query.filter_by(in_progress=True)
    check_list = [ Check(user.username, user.id, user.created_at, start_time) for user in users ]
    [ check.run() for check in check_list ]

    return render_template("admin/daily.html", users=check_list, is_today_checked=False, check_json=[ c.__dict__ for c in check_list ], yesterday=yesterday_record, date=start_time )


@admin.route('/daily/post', methods=['POST'])
@admin_only
def daily_check_post():
    data_list = loads(request.form['check'])
    day = date.today() - timedelta(1) if request.form['yesterday'] == 'True' else date.today()
    for check in data_list:
        new_check = DailyCheck(
            user_id = check['user_id'],
            date = day,
            send_esm_count = check['send_esm_count'],
            esm_done_count = check['esm_done_count'],
            accessibility = check['accessibility'],
            no_result_lost = check['no_result_lost'],
            time_list = check['time_list'],
            im_notification_count = check['im_notification_count'],
            all_valid = check['all_valid'],
            result_incomplete = check['result_incomplete'],
            fail_list = check['fail_list'])
        db.session.add(new_check)
    db.session.commit()
    return "checked!"

@admin.route('/daily/user/<int:user_id>')
@admin_only
def check_user_daily(user_id):
    user_daily = DailyCheck.query.filter_by(user_id=user_id).order_by(DailyCheck.date.asc()).all()
    esm_done_mean = mean([ i.esm_done_count for i in user_daily ])
    contacts_query = ContactQuestionnaire.query.filter_by(user_id=user_id)
    contacts_count = contacts_query.count()
    completed_count = contacts_query.filter_by(completed=True).count()
    d = DeviceID.query.filter_by(user_id=user_id).first()
    if d:
        blacklists = db.session.query(ESMCount.name, func.count(ESMCount.name)).filter(ESMCount.device_id==d.device_id).group_by(ESMCount.name). order_by(desc(func.count(ESMCount.name))).limit(2).all()
        blacklist = []
        for b in blacklists:
         if b[1] > 5:
             blacklist.append(b[0])
    return render_template("admin/each_user_daily.html", blacklist=str(blacklist), checks=user_daily, username=User.query.filter_by(id=user_id).first().username, mean=esm_done_mean, contacts_count=contacts_count, completed_count=completed_count)
