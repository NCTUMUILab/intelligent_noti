from datetime import datetime, date, timedelta
from json import dumps
import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))
from app.models import DailyCheck, User, DeviceID, Notification, Result, DailyCheck
from app.helpers.daily_check import Check

user_list = User.query.filter(User.id >= 5).filter(User.id < 6).all()
for user in user_list:
    print(user.id)
    start_time = datetime.combine(user.created_at, datetime.min.time())
    while start_time != datetime.combine(date.today(), datetime.min.time()):
        print("STARTTIME:", start_time)
        check = Check(user.username, user.id, user.created_at, start_time)
        try:
            print("<{}>".format(check.name))
        except UnicodeError:
            print("<{}>".format(check.user_id))
        
        device_entry = DeviceID.query.filter_by(user_id=check.user_id).first()
        if device_entry:
            check.device_id = device_entry.device_id
        
        check.count_esm_done()
        
        noti_day_query = Notification.query.filter_by(device_id=check.device_id).filter(Notification.timestamp > check.start_time.timestamp() * 1000).filter(Notification.timestamp <= check.end_time.timestamp() * 1000)
        check.count_send_esm(noti_day_query)
        check.count_im_noti(noti_day_query)
        
        # result_day_query = Result.query.filter_by(user=check.device_id).filter(Result.date >= check.start_time).filter(Result.date < check.end_time)
        result_list = []
        result_prequery = Result.query.filter_by(user=check.device_id)
        for t in range(24):
            result_list.append(result_prequery.filter_by(date=check.start_time+timedelta(hours=t)).first())
        check.check_data(result_list)
        
        check.check_valid()
        check.fail_list = dumps(check.fail_list)
        print("\t{}, {}\n".format(check.all_valid, check.fail_list))
        
        new_daily = DailyCheck(user_id = check.user_id,
            date = check.start_time,
            send_esm_count = check.send_esm_count,
            esm_done_count = check.esm_done_count,
            accessibility = check.accessibility)
        # db.session.add(new_daily)
        
        
        start_time += timedelta(1)
# db.session.commit()




