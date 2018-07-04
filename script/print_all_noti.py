import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))
from app import db
from app.models import Result
from json import loads

rs = Result.query.filter_by(user=358099072596562)
for r in rs:
    noti_dict = loads(r.raw).get('Notification')
    if noti_dict:
        print(r.date, noti_dict['app_cols'])