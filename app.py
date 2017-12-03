from flask import render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

from models import app, db, User
from forms import LoginForm, RegisterForm, FacebookLoginForm
from login import login_manager, load_user
from get_facebook import fbMessenger, ThreadInfo


# init bootstrap
Bootstrap(app)

### route ###
@app.route('/')
def index():
	return render_template('index.html')

## User System ##
@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('dashboard'))
		else:
			return 'Invalid username or password'
	return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
	form = RegisterForm()
	
	if form.validate_on_submit():
		hashed_password = generate_password_hash(form.password.data, method='sha256')
		new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(new_user)
		db.session.commit()
		login_user(new_user)
		return redirect(url_for('dashboard'))
	
	return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
	return render_template('dashboard.html', name=current_user.username)

@app.route('/facebook', methods=['GET', 'POST'])
@login_required
def facebook():
	form = FacebookLoginForm()
	if form.validate_on_submit():
		return "asdf"
	
	return render_template('facebook_login.html', form=form)
	
	


if __name__ == '__main__':
	app.run(debug=True)