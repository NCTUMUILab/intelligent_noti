from flask import Blueprint, request, render_template, redirect, url_for
from app.models import DeviceID, ESMCount
from app import db
from datetime import datetime, timedelta

esm = Blueprint('esm', __name__)

@esm.route('/count', methods=['GET'])
def receive_count():
    device_id = request.args.get('device_id')
    contact_name = request.args.get('name')
    new_count = ESMCount(device_id=device_id, name=contact_name)
    db.session.add(new_count)
    db.session.commit()
    return redirect(url_for('esm.report', device_id=device_id))

@esm.route('/report')
def report():
    device_id = request.args.get('device_id')
    result = {}
    all_query = ESMCount.query.filter_by(device_id=device_id)
    if not device_id or not all_query:
        return "bad request"
    result['total'] = len(all_query.all())

    today_threshold = datetime.now() - timedelta(days=1)
    esm_one_day_all = all_query.filter(ESMCount.created_at > today_threshold).all()
    result['today'] = len(esm_one_day_all)

    week_threshold = datetime.now() - timedelta(days=7)
    esm_one_week_all = all_query.filter(ESMCount.created_at > week_threshold).all()
    result['7_days'] = len(esm_one_week_all)

    day_count = {}
    for esm in all_query.all():
        time_str = esm.created_at.strftime('%y-%m-%d')
        if time_str in day_count:
            day_count[time_str] += 1
        else:
            day_count[time_str] = 1
    day_valid = 0
    for day, count in day_count.items():
        day_valid += 1 if count >= 3 else 0
    result['day_valid'] = day_valid
    return render_template('report.html', result=result, device_id=device_id)
