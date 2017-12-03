from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

app = Flask(__name__)
app.config['SECRET_KEY'] = 'im_msg_web_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/alex/Documents/HCIproject/im_msg/web/database.db'
db = SQLAlchemy(app)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(15), unique=True)
	password = db.Column(db.String(80))
	email = db.Column(db.String(50), unique=True)
	
class Contact(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	user_id = db.Column(db.Integer)
	completed = db.Column(db.Boolean)