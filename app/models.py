from flask_login import UserMixin
from . import db
from flask import Flask
from datetime import datetime
import dateutil.parser

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    r_type = db.Column(db.String(256))
    user = db.Column(db.String(256)) # device_id
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
    self_q_completed = db.Column(db.Boolean)


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


class DeviceID(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    device_id = db.Column(db.String(30))
    is_active = db.Column(db.Boolean)


class ESMCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.now)
    name = db.Column(db.String(30))

class ESMData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    StartDate = db.Column(db.DateTime)
    EndDate= db.Column(db.DateTime)
    Status= db.Column(db.String(30))
    IPAddress= db.Column(db.String(30))
    Progress= db.Column(db.String(30))
    Duration= db.Column(db.String(30))
    Finished= db.Column(db.String(30))
    RecordedDate= db.Column(db.DateTime)
    ResponseId= db.Column(db.String(30))
    RecipientLastName= db.Column(db.String(30))
    RecipientFirstName= db.Column(db.String(30))
    RecipientEmail= db.Column(db.String(30))
    ExternalReference= db.Column(db.String(30))
    LocationLatitude= db.Column(db.String(30))
    LocationLongitude= db.Column(db.String(30))
    DistributionChannel= db.Column(db.String(30))
    UserLanguage= db.Column(db.String(30))
    Q1= db.Column(db.String(30))
    Q2= db.Column(db.String(30))
    Q3= db.Column(db.String(30))
    Q4= db.Column(db.String(30))
    Q5= db.Column(db.String(30))
    Q6= db.Column(db.String(30))
    Q7= db.Column(db.String(30))
    Q8= db.Column(db.String(30))
    Q9= db.Column(db.String(30))
    Q10= db.Column(db.String(30))
    Q11= db.Column(db.String(30))
    Q12= db.Column(db.String(30))
    Q13= db.Column(db.String(30))
    Q14= db.Column(db.String(30))
    Q15= db.Column(db.String(30))
    Q16= db.Column(db.String(30))
    Q17= db.Column(db.String(30))
    Q18= db.Column(db.String(30))
    app= db.Column(db.String(30))
    title= db.Column(db.String(1024))
    text= db.Column(db.String(1024))
    created_at= db.Column(db.String(30))
    user= db.Column(db.String(30))
    time= db.Column(db.String(30))
    test= db.Column(db.String(30))
    Q5Topics= db.Column(db.String(30))
    textTopics= db.Column(db.String(30))
    app = db.Column(db.String(10))
