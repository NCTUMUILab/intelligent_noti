from flask_login import UserMixin
from . import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import dateutil.parser


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    r_type = db.Column(db.String(256))
    user = db.Column(db.String(256))
    r_id = db.Column(db.Integer)
    raw = db.Column(db.Text)
    date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, r):
        self.r_type = r['type']
        self.user = r['user']
        self.r_id = r['id']
        self.raw = r['raw']
        self.date = dateutil.parser.parse(r['date'])

    def __repr__(self):
        return '<Result %r>' % self.id

class FormResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wid = db.Column(db.Integer)
    user = db.Column(db.String(256))
    hash = db.Column(db.String(256))
    sender = db.Column(db.String(256))
    app = db.Column(db.String(256))
    raw = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, r):
        self.wid = r['wid']
        self.user = r['user']
        self.raw = r['raw']
        self.hash = r['hash']
        self.sender = r['sender']
        self.app = r['app']

class WhiteList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(256))
    facebook = db.Column(db.String(256))
    line = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.now)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(50), unique=True)
    phone_id = db.Column(db.String(30))

class ContactQuestionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_name = db.Column(db.String(50))
    contact_name_line = db.Column(db.String(50))
    user_id = db.Column(db.Integer)
    is_group = db.Column(db.Boolean) # deprecated
    completed = db.Column(db.Boolean)
    data = db.Column(db.Text)

class UserQuestionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True)
    completed = db.Column(db.Boolean)
    data = db.Column(db.Text)

class GpsLabel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    label = db.Column(db.String(256))
