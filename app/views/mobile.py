from flask import Blueprint, request, jsonify, render_template
from app.models import Result, User, ContactQuestionnaire, Notification
from app.helpers.valid_notification import valid_notification
from app import db
from app import app as flask_app
from datetime import datetime, timedelta
from sqlalchemy import desc
import hashlib
import json
import time
from datetime import timezone

from sqlalchemy.exc import IntegrityError
import uuid
from flask_cors import CORS, cross_origin
import dateutil.parser
from flask import abort

mobile = Blueprint('mobile', __name__)

def get_notification_data(user):
    delta = datetime.utcnow() - timedelta(minutes=5)
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
            try:
                p['white_list_user'] = db.session.query(ContactQuestionnaire).filter(ContactQuestionnaire.user_id==u.id).filter(ContactQuestionnaire.contact_name==p['title']).one_or_none()
            except Exception:
                p['white_list_user'] = None
            if not p['white_list_user'] and (not user == "c891e5cda613e2ac"):
                continue
    #        wids.append(p['white_list_user'].id)
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
            try:
                p['white_list_user'] = db.session.query(ContactQuestionnaire).filter(ContactQuestionnaire.user_id==u.id).filter(ContactQuestionnaire.contact_name_line==p['title']).one_or_none()
            except Exception:
                p['white_list_user'] = None
            if not p['white_list_user'] and (not user == "c891e5cda613e2ac"):
                continue
    #        wids.append(p['white_list_user'].id)
            p['wid'] = 0
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
    now = datetime.now()
    hour = now.hour
    if last_form:
        last_form_time = last_form.created_at
        last_form_sender = last_form.sender
    elif (hour >= 8 and hour <= 22) and contacts:
        return True
    else:
        return False

    delta_last_form =  now - last_form_time
    #if last_form_sender in contacts:
    #    contacts.remove(last_form_sender)
    if (hour >= 8 and hour <= 22) and (delta_last_form > timedelta(minutes=60)) and contacts:
        return True

    return False


@mobile.route('/upload/', methods=['POST'])
def add_result():
    content = request.get_json(silent=True)

    result = Result({
        'type': "new",
        'user': content['device_id'],
        'id': 0,
        'raw': json.dumps(content),
        'date' : content['startTimeString'] })
    db.session.add(result)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        abort(404)

    raw = content.get('Notification')
    if raw:
        for lat, sub_text, app, timestamp, text, lon, title, ticker, send_esm in \
            zip(raw['latitude_cols'], raw['subText_cols'], raw['app_cols'], raw['timestamps'], \
                raw['n_text_cols'], raw['longitude_cols'], raw['title_cols'], raw['tickerText_cols'], \
                raw['sendForm_cols']):
            # if ticker and (app=='com.facebook.orca' or app=='jp.naver.line.android'):
            try:
                flask_app.logger.info('<Noti> {}:{}, RESULT={}'.format(content['device_id'], ticker, valid_notification(app, ticker, title, text, sub_text)))
            if valid_notification(app, ticker, title, text, sub_text):
                new_notification = Notification(
                    timestamp = timestamp,
                    device_id = content['device_id'],
                    latitude = lat,
                    longitude = lon,
                    app = app,
                    title = title,
                    sub_text = sub_text,
                    text = text,
                    ticker_text = ticker,
                    send_esm = True if send_esm == '1' else False)
                db.session.add(new_notification)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
    return jsonify({
        'startTime': int(content['startTime']),
        'endTime': int(content['endTime'] ) })


@mobile.route('/state/', methods=['GET'])
def get_state():
     content = request.get_json(silent=True)
     user = request.args.get('user')
     last_result = db.session.query(Result).filter(Result.user==user).order_by(desc(Result.created_at)).first()
     if last_result:
        return str(int(datetime.fromtimestamp(int(json.loads(last_result.raw)['endTime'])/1000).replace(minute=0, second=0).strftime('%s'))*1000)
     else:
        return str((int(datetime.fromtimestamp(time.time()).replace(minute=0, second=0). strftime('%s'))-172800)*1000)
