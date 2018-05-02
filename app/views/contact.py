from flask import Blueprint, render_template, make_response, request, redirect, url_for, jsonify, abort
from flask_login import login_required, current_user
from app.models import ContactQuestionnaire, User
from app.forms import FacebookLoginForm, FacebookResultForm
from app.get_facebook import fbMessenger, ThreadInfo
# from app.helpers import find_questionnaire
from app import db, on_local
from json import loads, dumps

contact = Blueprint('contact', __name__)

    
@contact.route('/facebook/login', methods=['GET', 'POST'])
@login_required
def facebook_login():
    is_summited = ContactQuestionnaire.query.filter_by(user_id=current_user.id).first()
    if is_summited:
        return make_response(render_template('403_forbidden.html', current_user=current_user, message="You can't re-summit your facebook account!"), 403)

    form = FacebookLoginForm()
    if form.validate_on_submit():
        print("start scanning fbMessenger")
        ### FACEBOOK LOGIN ###
        fb = fbMessenger(form.account.data, form.password.data)
        contacts = fb.get_messages()
        contacts = sorted(contacts, reverse=True, key=lambda c: c.msg_count)
        return render_template('contact_list.html', current_user=current_user, contacts=contacts, limit=20)
    else:
        return render_template('facebook_login.html', form=form)
        

@contact.route('/confirm', methods=['POST'])
@login_required
def confirmContacts():
    is_summited = ContactQuestionnaire.query.filter_by(user_id=current_user.id).first()
    if is_summited:
        template = render_template('403_forbidden.html', current_user=current_user, message="You can't re-summit your facebook account!")
        return make_response(template, 403)
        
    contact_name_list = request.form.getlist('select')
    for name in contact_name_list:
        facebook_name = name.split('||')[0] if '||' in name else name
        line_name     = name.split('||')[1] if '||' in name else ""

        new_questionnaire = ContactQuestionnaire(
            contact_name=facebook_name,
            contact_name_line=line_name,
            user_id=current_user.id,
            is_group=False,
            completed=False)
        db.session.add(new_questionnaire)
        db.session.commit()
    return redirect(url_for('user.dashboard'))
    

@contact.route('/upload', methods=['GET', 'POST'])
@login_required
def uploadFacebookResult():
    is_summited = ContactQuestionnaire.query.filter_by(user_id=current_user.id).first()
    if is_summited:
        return make_response(render_template('403_forbidden.html', current_user=current_user, message="You can't re-summit your facebook account"), 403)
    
    form = FacebookResultForm()
    if form.validate_on_submit():
        result_facebook_str = form.file_facebook.data.read().decode('utf-8')
        result_list = loads(result_facebook_str)
        if form.file_line.data:
            result_line_str = form.file_line.data.read().decode('utf-8')
            result_list.extend(loads(result_line_str))
            
        result_list = sorted(result_list, reverse=True, key=lambda c: c['msg_count'])
        return render_template(
            'contact_list.html', 
            current_user=current_user, 
            contacts=result_list, 
            limit=20,
            pre_selected=20)
        
    return render_template('upload_result.html', form=form)


@contact.route('/add', methods=['GET', 'POST'])
@login_required
def addContact():
    if request.method == 'GET':
        contact_list = ContactQuestionnaire.query.filter_by(user_id=current_user.id).all()
        return render_template('add_new_contact.html', contact_list=contact_list)
    
    elif request.method == 'POST':
        print("fff")
        print("<{}>".format(request.form['facebook']))
        print("<{}>".format(request.form['line']))
        new_contact = ContactQuestionnaire(
            contact_name = request.form['facebook'],
            contact_name_line = request.form['line'],
            user_id = current_user.id,
            is_group = False,
            completed = False )
        print(1)
        db.session.add(new_contact)
        print(2)
        db.session.commit()
        print(new_contact)
        return redirect(url_for('contact.addContact'))


@contact.route('/remove/<int:qid>', methods=['POST'])
@login_required
def remove_contact(qid):
    contact = ContactQuestionnaire.query.filter_by(id=qid).first()
    if contact and contact.user_id == current_user.id:
        db.session.delete(contact)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
    else:
        abort(403)
    return redirect(url_for('contact.addContact'))


@contact.route('/getJson')
def get_contact_json():
    email = request.args.get('email')
    user = User.query.filter_by(email=email).first()
    if not user:
        abort(403)
    user_name = user.username
    contacts = ContactQuestionnaire.query.join(User).filter(User.email == email).all()
    contact_list = [ {'facebook': contact.contact_name, 'line': contact.contact_name_line} for contact in contacts ]
    return jsonify({'name': user_name, 'list': contact_list})