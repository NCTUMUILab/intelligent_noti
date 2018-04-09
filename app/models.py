from flask_login import UserMixin
from . import db
from flask import Flask
from datetime import datetime
import dateutil.parser


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(50), unique=True)
    self_q_completed = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.now)
    in_progress = db.Column(db.Boolean)


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    r_type = db.Column(db.String(256))
    user = db.Column(db.String(256)) # device_id
    r_id = db.Column(db.Integer)
    raw = db.Column(db.Text)
    date = db.Column(db.DateTime) # time of get sensor data
    created_at = db.Column(db.DateTime, default=datetime.now) # time of upload data

    def __init__(self, r):
        self.r_type = r['type']
        self.user = r['user']
        self.r_id = r['id']
        self.raw = r['raw']
        self.date = dateutil.parser.parse(r['date'])

    def __repr__(self):
        return '<Result %r>' % self.id


class ContactQuestionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_name = db.Column(db.String(50))
    contact_name_line = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    is_group = db.Column(db.Boolean) # deprecated
    completed = db.Column(db.Boolean)
    data = db.Column(db.Text)


class GpsLabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    label = db.Column(db.String(256))


class DeviceID(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    device_id = db.Column(db.String(30))
    is_active = db.Column(db.Boolean)


class ESMCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.now)
    name = db.Column(db.String(30))
    app = db.Column(db.String(10))


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.now)
    timestamp = db.Column(db.String(16))
    latitude  = db.Column(db.String(16))
    longitude = db.Column(db.String(16))
    app = db.Column(db.String(128))
    title = db.Column(db.String(128)) # usually sender name
    sub_text = db.Column(db.String(32)) # idk, usually none
    text = db.Column(db.Text) # text
    ticker_text = db.Column(db.Text) # text shown on screen (sender+text)
    send_esm = db.Column(db.Boolean) # if esm is sent

class DailyCheck(db.Model):
    __tablename__ = 'daily_check'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    date = db.Column(db.Date)
    send_esm_count = db.Column(db.Integer)
    esm_done_count = db.Column(db.Integer)
    im_notification_count = db.Column(db.Integer)
    phone_data_count = db.Column(db.Integer)
    all_valid = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.now)