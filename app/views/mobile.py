from flask import Blueprint, request, jsonify, render_template
from app.models import FormResult, Result, User, ContactQuestionnaire
from app import db
from datetime import datetime, timedelta
from sqlalchemy import desc
import hashlib

from sqlalchemy.exc import IntegrityError
import uuid
from flask_cors import CORS, cross_origin
import dateutil.parser


mobile = Blueprint('mobile', __name__)

def get_notification_data(user):
    delta = datetime.utcnow() - timedelta(minutes=30)
    u = db.session.query(User).filter(User.phone_id==user).one_or_none()

    notification_line = db.session.query(Result).filter(Result.date > delta).filter(Result.r_type == 'Notification').filter(Result.raw.like('jp.naver.line.android%')).filter(Result.user == user).order_by(desc(Result.created_at)).all()
    notification_fb = db.session.query(Result).filter(Result.date > delta).filter(Result.r_type == 'Notification').filter(Result.raw.like('com.facebook.orca%')).filter(Result.user == user).order_by(desc(Result.created_at)).all()
    db.session.close()
    notifications = []
    wids = []
    for n in notification_fb:
        noti = n.raw.split('\t')
        p = {}
        if noti[0] == 'com.facebook.orca':
            p['app'] = 'Facebook'
            p['title'] = noti[1]
            p['content'] = noti[2]
            p['time'] = n.date + timedelta(hours=8)
            p['white_list_user'] = db.session.query(ContactQuestionnaire).filter(ContactQuestionnaire.user_id==u.id).filter(ContactQuestionnaire.contact_name==p['title']).one_or_none()
            if not p['white_list_user']:
                continue
            wids.append(p['white_list_user'].id)
            p['wid'] = p['white_list_user'].id
            p['hash'] = hashlib.md5((str(noti[0:2]) + str(n.date)).encode()).hexdigest()
            p['done'] = bool(db.session.query(FormResult).filter(FormResult.hash==p['hash']).one_or_none())
            notifications.append(p)
    for n in notification_line:
        noti = n.raw.split('\t')
        p = {}
        if noti[0] == 'jp.naver.line.android':
            p['app'] = 'Line'
            p['title'] = noti[1]
            p['content'] = noti[2]
            p['time'] = n.date + timedelta(hours=8)
            p['white_list_user'] = db.session.query(ContactQuestionnaire).filter(ContactQuestionnaire.user_id==u.id).filter(ContactQuestionnaire.contact_name_line==p['title']).one_or_none()
            if not p['white_list_user']:
                continue
            wids.append(p['white_list_user'].id)
            p['wid'] = p['white_list_user'].id
            p['hash'] = hashlib.md5((str(noti[0:2]) + str(n.date)).encode()).hexdigest()
            p['done'] = bool(db.session.query(FormResult).filter(FormResult.hash==p['hash']).one_or_none())
            notifications.append(p)
    notifications = reversed(sorted(notifications, key=lambda k: k['time']))
    return list(notifications)

def get_form_valid(notifications, user):
    contacts = []
    for n in notifications:
        contacts.append(n['title'])
    contacts = list(set(contacts))
    last_form = db.session.query(FormResult).filter(FormResult.user==user).order_by(desc(FormResult.created_at)).first()
    if last_form:
        last_form_time = last_form.created_at
        last_form_sender = last_form.sender
    now = datetime.now()
    hour = now.hour
    delta_last_form =  now - last_form_time
    if (hour >= 8 and hour <= 22) and (delta_last_form > timedelta(minutes=180)) and contacts:
        return True
    if last_form_sender in contacts:
        contacts.remove(last_form_sender)
    if (hour >= 8 and hour <= 22) and (delta_last_form > timedelta(minutes=90)) and contacts:
        return True

    return False

@mobile.route('/form/', methods=['POST'])
def add_form():
    content = request.get_json(silent=True)
    r = FormResult({'raw': str(content), 'wid': content['wid'], 'user': content['user'], 'hash': content['hash'], 'sender': content['title'], 'app': content['app']})
    db.session.add(r)
    try:
        db.session.commit()
        msg = 'ok'
    except Exception as e:
         print(e)
         db.session.rollback()
         msg = 'error'
    return jsonify({'msg': msg})


@mobile.route('/upload/', methods=['POST'])
def add_result():
    content = request.get_json(silent=True)
    print('len: ', len(content))
    print('first id:', content[0]['id'])
    for c in content:
        result = Result(c)
        db.session.add(result)
        try:
            db.session.commit()
            msg = 'ok'
        except Exception as e:
            print(e)
            db.session.rollback()
            msg = 'error'
    if content:
        user = content[0]['user']
    last_form = db.session.query(FormResult).filter(FormResult.user==user).order_by(desc(FormResult.created_at)).first()
    if last_form:
        last_form = last_form.created_at

    notifications = get_notification_data(user)
    form_valid = get_form_valid(notifications, user)

    return jsonify({'msg': 'ok', 'last_form': last_form, 'form_valid': form_valid})


@mobile.route('/notification/')
def get_notification():
    user = request.args.get('user')

    notifications = get_notification_data(user)
    form_valid = get_form_valid(notifications, user)
    if len(notifications) > 10:
        notifications = notifications[0:10]
    msg = ""
    if len(notifications) == 0:
        msg = '現在沒有問卷喔!'
    return render_template('notification.html', notification=notifications, msg=msg, count=len(notifications))
