from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique=True)
	password = db.Column(db.String(80))
	email = db.Column(db.String(50), unique=True)

class ContactQuestionnaire(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	contact_name = db.Column(db.String(50))
	user_id = db.Column(db.Integer)
	is_group = db.Column(db.Boolean)
	completed = db.Column(db.Boolean)
	data = db.Column(db.Text)

class UserQuestionnaire(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, unique=True)
	completed = db.Column(db.Boolean)
	data = db.Column(db.Text)
