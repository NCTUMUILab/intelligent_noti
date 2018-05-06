from app.models import DailyCheck, ESMCount
from app.helpers.valid_notification import valid_notification
from datetime import datetime, timedelta
from json import dumps, loads

class CheckManager:
    def __init__(self, users, start_time):
        self.check_list = [ Check(user.username, user.id, user.created_at, start_time) for user in users ]
    
    def run(self):
        for check in self.check_list:
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
            
            result_day_query = Result.query.filter_by(user=check.device_id).filter(Result.date >= check.start_time).filter(Result.date < check.end_time)
            check.check_data(result_day_query.all())
            
            check.check_valid()
            check.fail_list = dumps(check.fail_list)
            print("\t{}, {}\n".format(check.all_valid, check.fail_list))
        
        return self.check_list

class Check:
    """
    check record for each day of each user
    """
    def __init__(self, name, user_id, user_created_at, start_time):
        self.start_time = start_time
        self.end_time = start_time + timedelta(1)
        
        self.name = name
        self.user_id = user_id
        self.device_id = ''
        self.day = (datetime.now().date() - user_created_at.date()).days + 1
        self.send_esm_count = 0
        self.esm_done_count = 0
        self.im_notification_count = 0
        self.accessibility = False
        self.no_result_lost = True
        self.raw_error = []
        self.all_valid = True
        self.warning = False
        self.fail_list = []
    
    
    def count_esm_done(self):
        """
        filter condition: 1. device_id  2. in the time slot 
        """
        self.esm_done_count = ESMCount.query.filter_by(device_id=self.device_id).filter(ESMCount.created_at > self.start_time).filter(ESMCount.created_at <= self.end_time).count()
    
    def count_send_esm(self, noti_day_query):
        self.send_esm_count = noti_day_query.filter_by(send_esm=True).count()
    
   
    def count_im_noti(self, noti_day_query):
        for each_noti in noti_day_query.filter_by(send_esm=False).all():
            if valid_notification(each_noti.app, each_noti.ticker_text, each_noti.title, each_noti.text, each_noti.sub_text):
                self.im_notification_count += 1
    
   
    # def _result_attrs_exist(self, raw_dict, *attrs):
    #     for attr in attrs:
    #         content = raw_dict.get(attr)
    #         if content:
    #             ts_list = content['timestamp'] if attr == 'sensor' else content['timestamps']
    #             if len(ts_list) < 3:
    #                 self.raw_error.append(attr)
    #         else:
    #             self.raw_error.append(attr)
        
    
    def check_data(self, day_all_result):
        time_list = [ 0 for i in range(24) ]
        for each_result in day_all_result:
            hour = int(each_result.date.strftime("%H"))
            time_list[hour] += 1
            raw_dict = loads(each_result.raw)
            # print(raw_dict['startTimeString'], len(raw_dict))
            if len(raw_dict) <= 5:
                self.raw_error.append(raw_dict['startTimeString'])
            if raw_dict.get("Accessibility"):
                self.accessibility = True
            self._result_attrs_exist(raw_dict, "AppUsage", "Battery", "Connectivity", "Location", "Ringer", "sensor")
        
        print('\t{}'.format(time_list))
        if self.day == 1: # must lost some data in day one, so ignore it
            return
        zero_start = False
        result_exist = False
        for each_count in time_list:
            if each_count != 0:
                result_exist = True
            if each_count == 0:
                zero_start = True
            elif each_count != 0 and zero_start:
                print('\terror in result')
                self.no_result_lost = False
                return
        if not result_exist:
            self.no_result_lost = False
    
    
    def check_valid(self):
        if self.esm_done_count < 5 and self.day > 1:
            self.all_valid = False
            self.fail_list.append('esm_done_count')
        if not self.accessibility:
            self.all_valid = False
            self.fail_list.append('accessibility')
        if not self.no_result_lost:
            self.all_valid = False
            self.fail_list.append('no_result_lost')
        if self.raw_error:
            self.all_valid = False
            self.fail_list.append(self.raw_error)
        
        if not self.all_valid:
            last_check = DailyCheck.query.filter_by(user_id=self.user_id).order_by(DailyCheck.date.desc()).first()
            if last_check and not last_check.all_valid:
                self.warning = True
            else:
                self.warning = False
        
    
def is_today_checked():
    last_check = DailyCheck.query.order_by(DailyCheck.created_at.desc()).first()
    if last_check and last_check.created_at.date() == datetime.now().date():
        return True
    return False