from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo, ValidationError
from .models import User

class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired()])
	remember = BooleanField('remember me')

def unique_username(form, field):
	if User.query.filter_by(username=field.data).first():
		raise ValidationError('Username has been used')

def unique_email(form, field):
	if User.query.filter_by(email=field.data).first():
		raise ValidationError('Email has been used')

class RegisterForm(FlaskForm):
	email = StringField('email', validators=[InputRequired(), Email(message="Invalid email"), Length(max=50), unique_email])
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15), unique_username])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80), EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password')
	
class FacebookLoginForm(FlaskForm):
	account = StringField('Email or Phone number', validators=[InputRequired()])
	password = PasswordField('Password', validators=[InputRequired()])