import sys
import os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join('..')))
from app import db
from app.models import Notification

notifications = Notification.query.all()


for notification in notifications:
    print(notification.datetime)
    notification.datetime = datetime.fromtimestamp(int(notification.timestamp)/1000)

    print(notification.datetime)
db.session.commit()
