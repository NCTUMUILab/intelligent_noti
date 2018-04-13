from app.models import DailyCheck
from datetime import datetime

def check_valid(check):
    record_valid = True
    if check['im_notification_count'] <= 10:
        record_valid = False
        check['fail_list'].append('im_notification_count')
    if check['send_esm_count'] <= 5:
        record_valid = False
        check['fail_list'].append('send_esm_count')
    if check['esm_done_count'] <= 5:
        record_valid = False
        check['fail_list'].append('esm_done_count')
    if not check['accessibility']:
        record_valid = False
        check['fail_list'].append('accessibility')
    if not check['no_result_lost']:
        record_valid = False
        check['fail_list'].append('no_result_lost')
    return record_valid

    
def is_today_checked():
    last_check = DailyCheck.query.order_by(DailyCheck.created_at.desc()).first()
    if last_check and last_check.created_at.date() == datetime.now().date():
        return True
    return False


def two_days_fail(user_id):
    last_check = DailyCheck.query.filter_by(user_id=user_id).order_by(DailyCheck.created_at.desc()).first()
    if last_check and not last_check.all_valid:
        return True
    return False


def check_result_lost(today_all_result):
    time_list = [ 0 for i in range(24) ]
    for result in today_all_result:
        hour = int(result.date.strftime("%H"))
        time_list[hour] += 1
    zero_start = False
    for time in time_list:
        if time == 0:
            zero_start = True
        elif time != 0 and zero_start:
            return False
    return True