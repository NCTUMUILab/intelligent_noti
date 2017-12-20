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
    result = db.session.query(FormResult).filter(FormResult.user).order_by(desc(FormResult.created_at)).first()
    if result:
        result = result.created_at
    print({'msg': 'ok', 'last_form': result})
    return jsonify({'msg': 'ok', 'last_form': result})


@mobile.route('/notification/')
def get_notification():
    delta = datetime.utcnow() - timedelta(minutes=600)
    user = request.args.get('user')
    u = db.session.query(User).filter(User.phone_id==user).one_or_none()
    notification = db.session.query(Result).filter(Result.r_type == 'Notification').filter(Result.user == user).filter(Result.date > delta).order_by(desc(Result.created_at)).all()
    db.session.close()
    notifications = []
    wids = []
    for n in notification:
        noti = n.raw.split('\t')
        p = {}
        if noti[0] == 'com.facebook.orca':
            p['app'] = 'Facebook'
            p['title'] = noti[1]
            p['content'] = noti[2]
            p['time'] = n.date
            p['white_list_user'] = db.session.query(ContactQuestionnaire).filter(ContactQuestionnaire.user_id==u.id).filter(ContactQuestionnaire.contact_name==p['title']).one_or_none()

            if not p['white_list_user']:
                continue
            wids.append(p['white_list_user'].id)
            p['wid'] = p['white_list_user'].id
            p['hash'] = hashlib.md5((str(noti[0:2]) + str(n.date)).encode()).hexdigest()
            p['done'] = bool(db.session.query(FormResult).filter(FormResult.hash==p['hash']).one_or_none())
            notifications.append(p)
    notifications = sorted(notifications, key=lambda k: k['time'])
    wid_count = {}
    for wid in wids:
        wid_count[wid] = db.session.query(FormResult).filter(FormResult.wid==wid).count()
    _wid_count = wid_count
    wid_count = sorted(wid_count, key=wid_count.get)
    selected = []
    for w in wid_count[0:3]:
        for n in notifications:
            if n['wid'] == w:
                selected.append(n)
                break
    return render_template('notification.html', notification=selected, wid_count=_wid_count)