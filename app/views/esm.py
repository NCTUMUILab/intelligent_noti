from flask import Blueprint, request, render_template, redirect, url_for
from app.models import DeviceID, ESMCount
from app import db
from datetime import datetime, timedelta, date

esm = Blueprint('esm', __name__)

@esm.route('/count', methods=['GET'])
def receive_count():
    device_id = request.args.get('device_id')
    contact_name = request.args.get('name')
    app = request.args.get('app')
    new_count = ESMCount(device_id=device_id, name=contact_name, app=app)
    db.session.add(new_count)
    db.session.commit()
    return redirect(url_for('esm.report', device_id=device_id))

@esm.route('/report')
def report():
    device_id = request.args.get('device_id')
    if not device_id:
        return "bad request"
    # if not DeviceID.query.filter_by(device_id=device_id).first():
    #     return "invalid device ID"
    
    report = {}
    all_query = ESMCount.query.filter_by(device_id=device_id)
    report['total'] = all_query.count()

    today_threshold = datetime.combine(date.today(), datetime.min.time())
    report['today'] = all_query.filter(ESMCount.created_at > today_threshold).count()

    week_threshold = datetime.now() - timedelta(days=7)
    report['7_days'] = esm_one_week_all = all_query.filter(ESMCount.created_at > week_threshold).count()
    
    app_count = { 'fb': 0, 'line': 0 }
    sender_count = {}
    for esm in all_query.all():
        app_count[esm.app] += 1
        if esm.name in sender_count:
            sender_count[esm.name] += 1
        else:
            sender_count[esm.name] = 1
    sender_count = [ {"name":sender, "count":value} for sender, value in sender_count.items() ]
    
    return render_template('report.html', result=report, device_id=device_id, app_count=app_count, sender_count=sender_count)
