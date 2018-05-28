from app.models import DailyCheck, ESMCount, DeviceID, Notification, Result
from helpers.valid_notification import valid_notification
from datetime import datetime, timedelta
from json import dumps, loads


class Check:
    """
    check record for each day of each user
    """
    def __init__(self, name, user_id, user_created_at, start_time):
        self.start_time = start_time
        self.end_time = start_time + timedelta(1)
        
        self.name = name
        self.user_id = user_id
        self.device_id = self._get_device_id()
        self.day = (datetime.now().date() - user_created_at.date()).days + 1
        self.send_esm_count = 0
        self.esm_done_count = 0
        self.im_notification_count = 0
        self.accessibility = False
        self.noti_alive = False
        self.no_result_lost = True
        self.result_incomplete = []
        self.time_list = []
        self.all_valid = True
        self.warning = False
        self.fail_list = []
    
    
    def _count_esm_done(self):
        """filter condition: 1. device_id  2. in the certain day """
        return ESMCount.query.filter_by(device_id=self.device_id).filter(ESMCount.created_at > self.start_time).filter(ESMCount.created_at <= self.end_time).count()
    
    def _count_send_esm(self, noti_day_query):
        return noti_day_query.filter_by(send_esm=True).count()
    
   
    def _count_im_noti(self, noti_day_query):
        count = 0
        for each_noti in noti_day_query.filter_by(send_esm=False):
            if valid_notification(each_noti.app, each_noti.ticker_text, each_noti.title, each_noti.text, each_noti.sub_text):
                count += 1
        return count
    
   
    def _result_attr_exist(self, result_incomplete, raw_dict, attr):
        content = raw_dict.get(attr)
        if content:
            ts_list = content['timestamp'] if attr == 'sensor' else content['timestamps']
            if len(ts_list) < 60:
                result_incomplete.append("{}_{}_{}".format(attr,raw_dict['startTimeString'][11:13], len(ts_list)))
        else:
            result_incomplete.append("{}_{}_None".format(attr,raw_dict['startTimeString'][11:13]))
        return result_incomplete
        
    
    def _check_sensor_data(self):
        ret = {
            'acc': False,
            'noti_alive': False,
            'no_result_lost': True,
            'result_incomplete': [],
            'time_list': [ 0 for i in range(24) ] }
        
        result_day_query = Result.query.filter_by(user=self.device_id).filter(Result.date >= self.start_time, Result.date < self.end_time)
        for each_result in result_day_query:
            hour = int(each_result.date.strftime("%H"))
            ret['time_list'][hour] += 1
            if ret['time_list'][hour] == 1:
                raw_dict = loads(each_result.raw)
                if raw_dict.get("Accessibility"):
                    ret['acc'] = True
                if raw_dict.get("Notification"):
                    ret['noti_alive'] = True
                if 10 <= int(raw_dict['startTimeString'][11:13]) <= 22:
                    self._result_attr_exist(ret['result_incomplete'], raw_dict, "AppUsage")
        if 0 in ret['time_list']:
            ret['no_result_lost'] = False        
        return ret
    
    
    def _check_valid(self):
        if self.esm_done_count < 5 and self.day > 1:
            self.fail_list.append('esm_done_count')
        if not self.accessibility:
            self.fail_list.append('accessibility')
        if not self.noti_alive:
            self.fail_list.append('noti_alive')
        if not self.no_result_lost:
            self.fail_list.append('no_result_lost')
        if len(self.result_incomplete) > 2:
            self.fail_list.append("result_incomplete")
        
        if self.fail_list:
            self.all_valid = False
        
            last_check = DailyCheck.query.filter_by(user_id=self.user_id).order_by(DailyCheck.date.desc()).first()
            if last_check and not last_check.all_valid:
                self.warning = True
            else:
                self.warning = False
    
    
    def _get_device_id(self):
        device_entry = DeviceID.query.filter_by(user_id=self.user_id).first()
        if device_entry:
            return device_entry.device_id
        else:
            raise ValueError
    
    
    def _dumps(self):
        self.result_incomplete = dumps(self.result_incomplete)
        self.fail_list = dumps(self.fail_list)
        self.time_list = dumps(self.time_list)
    
    
    def run(self):
        try:
            print("<{} : {}>".format(self.name, self.start_time.strftime("%m-%d")))
        except UnicodeError:
            print("<{} : {}>".format(self.user_id, self.start_time.strftime("%m-%d")))
        
        self.esm_done_count = self._count_esm_done()
        
        noti_day_query = Notification.query.filter_by(device_id=self.device_id).filter(Notification.timestamp > self.start_time.timestamp() * 1000).filter(Notification.timestamp <= self.end_time.timestamp() * 1000)
        self.send_esm_count = self._count_send_esm(noti_day_query)
        self.im_notification_count = self._count_im_noti(noti_day_query)
        print("\tSEND: {}, DONE: {}, NOTI: {}".format(self.send_esm_count, self.esm_done_count, self.im_notification_count))
        
        check_sensor_dict = self._check_sensor_data()
        self.accessibility = check_sensor_dict['acc']
        self.noti_alive = check_sensor_dict['noti_alive']
        self.no_result_lost = check_sensor_dict['no_result_lost']
        self.result_incomplete = check_sensor_dict['result_incomplete']
        self.time_list = check_sensor_dict['time_list']
        print('\t{}'.format(self.time_list))
        
        self._check_valid()
        if self.result_incomplete:
            print("\tRESULT INC:", self.result_incomplete)
        print("\tCHECK: {}\n".format(self.fail_list))
        
        self._dumps()
