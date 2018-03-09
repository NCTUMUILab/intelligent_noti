from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Result, GpsLabel, DeviceID
from sqlalchemy import desc
from flask import request
from json import loads

heatmap = Blueprint('heatmap', __name__)


@heatmap.route('/heatmap', methods=['GET', 'POST'])
@login_required
def show_heatmap():
	return render_template('heatmap.html')
	
@heatmap.route('/getLocations', methods=['GET', 'POST'])
def getLocationsTest():
	print('start')
	device_user = DeviceID.query.filter_by(user_id=current_user.id).first()
	print(current_user.id, device_user.device_id)
	all_result = Result.query.filter_by(user=device_user.device_id).all()
	marks = []
	for result in all_result:
		try:
			result_dict = loads(result.raw)
		except Exception as e:
			print("id:", result.id)
			print(e)
			continue
		if result_dict.get('Notification'):
			notification = result_dict['Notification']
			for app_source, lng, lag in zip(notification['app_cols'], notification['longitude_cols'], notification['latitude_cols']):
				if app_source == 'com.facebook.orca' or app_source == 'jp.naver.line.android':
					location = (lag, lng)
					marks.append(location)
					print(app_source, lag, lng)
	result_marks = {'marks': marks}
	return jsonify(result_marks)
	

@heatmap.route('/createGpsLabel', methods=['POST'])
def createGpsLabel():
	data = request.form.to_dict(flat=True)
	g = GpsLabel(user_id=current_user.id, lat=data['lat'], lng=data['lng'], label=data['label'])
	db.session.add(g)
	try:
		db.session.commit()
	except Exception as e:
		print(e)
		db.session.rollback()
	return 'ok'
	

@heatmap.route('/deleteGpsLabel', methods=['POST'])
def deleteGpsLabel():
    data = request.form.to_dict(flat=True)
    label = db.session.query(GpsLabel).filter(GpsLabel.id == data['markerId']).one_or_none()
    db.session.delete(label)
    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    return 'ok'
    
   
@heatmap.route('/listGpsLabel', methods=['GET'])
def listGpsLabel():
	locations = db.session.query(GpsLabel).filter(GpsLabel.user_id == current_user.id).all()
	result = []
	for location in locations:
		result.append({
			'lng': location.lng,
			'lat': location.lat,
			'label': location.label,
			'markerId': location.id
		})
	return jsonify(result)
