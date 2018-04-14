from app.models import DailyCheck
from datetime import datetime
from json import dumps

class Check:
    def __init__(self, name, user_id, created_at):
        self.name = name
        self.user_id = user_id
        self.device_id = ''
        self.day = (datetime.now()-created_at).days + 1
        self.send_esm_count = 0
        self.esm_done_count = 0
        self.im_notification_count = 0
        self.accessibility = False
        self.no_result_lost = None
        self.all_valid = True
        self.warning = False
        self.fail_list = []
    
    def toJSON(self):
         return dumps(self, default=lambda o: o.__dict__)
        
    def check_valid(self):
        if self.im_notification_count <= 10:
            self.all_valid = False
            self.fail_list.append('im_notification_count')
        if self.send_esm_count <= 5:
            self.all_valid = False
            self.fail_list.append('send_esm_count')
        if self.esm_done_count <= 5:
            self.all_valid = False
            self.fail_list.append('esm_done_count')
        if not self.accessibility:
            self.all_valid = False
            self.fail_list.append('accessibility')
        if not self.no_result_lost:
            self.all_valid = False
            self.fail_list.append('no_result_lost')

    
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