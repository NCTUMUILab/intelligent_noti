from flask import Blueprint, request, render_template, jsonify
from app.models import DeviceID, ESMCount
from app import db
from datetime import datetime, timedelta

esm = Blueprint('esm', __name__)

@esm.route('/count', methods=['POST'])
def receive_count():
	device_id = request.form['device_id']
	try:
		user_id = DeviceID.query.filter_by(device_id=device_id).first().user_id
	except:
		return "fail"
	new_count = ESMCount(user_id=user_id)
	db.session.add(new_count)
	db.session.commit()
	return "success"
	
@esm.route('/report')
def report():
	device_id = request.args.get('device_id')
	result = {}
	if not device_id:
		return "bad request"
	user_id = DeviceID.query.filter_by(device_id=device_id).first().user_id
	all_query = ESMCount.query.filter_by(user_id=user_id)
	result['all'] = len(all_query.all())
	
	time_threshold = datetime.now() - timedelta(days=7)
	esm_one_week_all = all_query.filter(ESMCount.created_at > time_threshold).all()
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
	return jsonify(result)