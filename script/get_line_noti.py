"""
Get LINE noti from a specific user in past 2 days, and print them out.
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))

from app.models import Result
from datetime import datetime, date, timedelta
from json import loads

results = Result.query.filter_by(user=355098061792896).filter(Result.date >= datetime.combine(date.today() - timedelta(2), datetime.min.time())).all()
for r in results:
	print(r.date)
	d = loads(r.raw)
	if d.get('Notification'):
		noti = d['Notification']
		for ticker, app in zip(noti['tickerText_cols'], noti['app_cols']):
			print("\t"+app)
	print()