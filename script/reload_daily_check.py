from datetime import datetime, date, timedelta
from json import dumps
import sys, os
sys.path.append(os.path.abspath(os.path.join('..')))
from app import db
from app.models import DailyCheck, User, DeviceID, Notification, Result, DailyCheck
from helpers.daily_check import Check
from sys import argv

def get_new_dailycheck(check):
    return DailyCheck(
        user_id = check.user_id,
        date = check.start_time,
        send_esm_count = check.send_esm_count,
        esm_done_count = check.esm_done_count,
        accessibility = check.accessibility,
        no_result_lost = check.no_result_lost,
        time_list = check.time_list,
        im_notification_count = check.im_notification_count,
        all_valid = check.all_valid,
        result_incomplete = check.result_incomplete,
        fail_list = check.fail_list)

def iterate_all_user():   
    user_list = User.query.filter(User.id >= 5).filter(User.id <= 10).filter_by(in_progress=True)
    for user in user_list:
        start_time = datetime.combine(user.created_at + timedelta(days=1), datetime.min.time())
        while start_time != datetime.combine(date.today(), datetime.min.time()):
            print("DATE:", start_time.strftime("%Y-%m-%d"))
            check = Check(user.username, user.id, user.created_at, start_time)
            check.run()
            
            new_daily = get_new_dailycheck(check)
            db.session.add(new_daily)
                       
            start_time += timedelta(days=1)
        db.session.commit()

def one_user(user_id, start_date, end_date, commit=True):
    date = datetime(2018, *start_date)
    while date != datetime(2018, *end_date):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise Exception
        previous_check = DailyCheck.query.filter_by(user_id=user_id, date=date).first()
        if previous_check:
            print(previous_check)
            db.session.delete(previous_check)
                
        check = Check(user.username, user_id, user.created_at, date)
        check.run()
        new_daily = get_new_dailycheck(check)
        db.session.add(new_daily)
        if commit:
            db.session.commit()
        
        date += timedelta(days=1)


if __name__ == '__main__':
    input("Check that db get all result packages\nPRESS ENTER TO CONT...")
    if len(argv) >= 5 and argv[1] == 'oneuser':
        start_date = [ int(i) for i in argv[3].split('/') ]
        end_date   = [ int(i) for i in argv[4].split('/') ]
        commit = False if len(argv) == 6 and argv[5] == 'nocommit' else True
        one_user(int(argv[2]), tuple(start_date), tuple(end_date), commit=commit)
    elif len(argv) == 2 and argv[1] == 'help':
        print("USAGE: python3 reload_daily_check.py oneuser 5(user_id) 5/12(start_date) 5/20(end_date)")

