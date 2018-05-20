from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Notification, GpsLabel, DeviceID
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
	device_user = DeviceID.query.filter_by(user_id=current_user.id).first()
	notis = Notification.query.filter_by(device_id=device_user.device_id)
	print("NOTI COUNT:", notis.count())
	marks = [ (noti.latitude, noti.longitude) for noti in notis ]
	return jsonify({'marks': marks})
	

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
