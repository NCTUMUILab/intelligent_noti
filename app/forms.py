from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo, ValidationError
from flask_wtf.file import FileField, FileRequired
from .models import User

class LoginForm(FlaskForm):
	email = StringField('電子信箱', validators=[InputRequired(), Email(message="格式不符合"), Length(max=50)])
	password = PasswordField('密碼', validators=[InputRequired()])
	remember = BooleanField('記住我')

def unique_username(form, field):
	if User.query.filter_by(username=field.data).first():
		raise ValidationError('Username has been used')

def unique_email(form, field):
	if User.query.filter_by(email=field.data).first():
		raise ValidationError('Email has been used')

def signup_secret_token(form, field):
	if not field.data == 'adminonly':
		raise ValidationError('No Permission')

class RegisterForm(FlaskForm):
	email = StringField('電子信箱', validators=[ InputRequired(), Email(message="Invalid email"), Length(max=50), unique_email ])
	username = StringField('真實姓名', validators=[ InputRequired(), unique_username ])
	password = PasswordField('密碼', validators=[ InputRequired(), EqualTo('confirm', message='Passwords must match') ])
	confirm = PasswordField('請再重複一次密碼', validators=[ InputRequired() ])
	device_id = StringField('Device ID', validators=[ InputRequired() ])
	secret_token = PasswordField('Secret Token', validators=[ InputRequired(), signup_secret_token ])
	
class FacebookLoginForm(FlaskForm):
	account = StringField('Email or Phone number', validators=[ InputRequired() ])
	password = PasswordField('Password', validators=[ InputRequired() ])
	
class FacebookResultForm(FlaskForm):
	file_facebook = FileField('result_facebook.txt', validators=[ FileRequired() ])
	file_line     = FileField('result_line.txt')

def check_mail_exist(form, field):
	if not User.query.filter_by(email=field.data).first():
		raise ValidationError('Invalid Email, Please contact admin.')

class ForgotPassword(FlaskForm):
	email = StringField('email', validators=[ InputRequired(), Email(message="Invalid email format"), check_mail_exist ])
	password = PasswordField('new_password', validators=[ InputRequired(), Length(min=8, max=80), EqualTo('confirm', message='Passowrds must match') ])
	confirm = PasswordField('Repeat Password', validators=[ InputRequired() ])