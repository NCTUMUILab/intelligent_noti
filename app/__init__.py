from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

Bootstrap(app)
db = SQLAlchemy(app)

# login-manage
from flask_login import LoginManager
from .models import User

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# decorators
from flask import redirect, url_for, make_response, render_template, current_app
from flask_login import current_user
from functools import wraps

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if getattr(current_user, "username", None) == "admin":
            return f(*args, **kwargs)
        else:
            return make_response(render_template('403_forbidden.html', current_user=current_user, message="You are not the ADMIN!"), 403)
    return decorated_function

def on_local(f):
    print("watttssss")
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("local:", current_app.config.get('LOCAL'))
        if current_app.config.get('LOCAL'):
            return f(*args, **kwargs)
        else:
            return make_response(render_template('403_forbidden.html', current_user=current_user, message="YOU SHALL NOT PASS"), 403)
    return decorated_function

# views
from .views.user import user
from .views.contact import contact
from .views.questionnaire import questionnaire
from .views.heatmap import heatmap
from .views.mobile import mobile
from .views.admin import admin
from .views.esm import esm

app.register_blueprint(user)
app.register_blueprint(contact, url_prefix='/contact')
app.register_blueprint(questionnaire)
app.register_blueprint(heatmap)
app.register_blueprint(mobile)
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(esm, url_prefix='/esm')