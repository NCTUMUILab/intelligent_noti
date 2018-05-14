import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))
from app import db
from app.models import Notification
from datetime import datetime

for i, noti in enumerate(Notification.query.filter_by(device_id=869589029598200)):
	date = datetime.fromtimestamp(int(noti.timestamp)/1000)
	print(date)
	noti.datetime = date
	if i % 50 == 0:
		db.session.commit()
db.session.commit()

# print(all_noti.id, all_noti.timestamp)
# d = datetime.fromtimestamp(int(all_noti.timestamp)/1000)
# print(d)




