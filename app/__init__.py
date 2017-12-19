from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

# Brootstrap, DebugToolbar, SQLAlchemy
Bootstrap(app)
# DebugToolbarExtension(app)
db = SQLAlchemy(app)

# login-manage
from flask_login import LoginManager
from .models import User

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

# admin
from flask import redirect, url_for, make_response, render_template
from flask_login import current_user
from functools import wraps

def admin_only(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if current_user.username == "admin":
			return f(*args, **kwargs)
		else:
			return make_response(render_template('403_forbidden.html', current_user=current_user, message="You are not the ADMIN!"), 403)
	return decorated_function

# views
from .view import *

