from os import listdir
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from json import dumps

class Thread(object):
    def __init__(self, beautiful_soup):
        self.soup = beautiful_soup
        self.user_name = self.soup.find('title').get_text()[18:]
        self.msg_count = 0
        self.day_count = 0
        self.last_time = None
        self.max_oneday = 0
        

class FacebookCounter(object):
    def __init__(self, directory):
        self.directory = directory
        self.file_list = []
        self.result = []
        self.time_threshold = datetime.now() - timedelta(days=30)
    
    def make_list(self):
        for file_name in listdir(self.directory):
            self.file_list.append(file_name)
        print('{} threads in total'.format( len(self.file_list) ))

    def count_messages(self, file_name):
        with open(self.directory+file_name, encoding='utf-8') as file:
            thread = Thread(BeautifulSoup(file.read(), 'html.parser'))
        
        if ',' in thread.user_name or thread.user_name == 'Facebook User' or not thread.user_name:
            return
        
        time_list = thread.soup.find_all('span', class_='meta') 
        last_day = None
        if time_list:
            last_time = datetime.strptime(time_list[0].get_text()+"00", '%A, %B %d, %Y at %I:%M%p %Z%z').replace(tzinfo=None)
            thread.last_time = datetime.strftime(last_time, '%Y/%m/%d')
        
        tmp_max_oneday = 0
        for index, time in enumerate(time_list): # each message time
            msg_time = datetime.strptime(time.get_text()+"00", '%A, %B %d, %Y at %I:%M%p %Z%z').replace(tzinfo=None)
            tmp_last_day = datetime.strftime(msg_time, '%Y %m %d')
            
            if msg_time > self.time_threshold: # desired time period
                thread.msg_count += 1
                if last_day != tmp_last_day: # different day
                    thread.day_count += 1
                    last_day = tmp_last_day
                    thread.max_oneday = max(thread.max_oneday, tmp_max_oneday)
                    tmp_max_oneday = 0
                else: # same day
                    tmp_max_oneday += 1
            else:
                break
        
        if thread.msg_count > 0:
            self.result.append( { 
                "user_name": thread.user_name, 
                'msg_count': thread.msg_count, 
                'day_count': thread.day_count,
                'last_time': thread.last_time,
                'max_oneday': thread.max_oneday,
                'app': 'facebook' } )
            self.print(thread_no=file_name[:-5], thread=thread)
            
    def print(self, thread_no, thread):
        print('Thread: {}'.format(thread_no))
        print('User: {}'.format(thread.user_name))
        print('Message Count: {}'.format(thread.msg_count))
        print('Day Count: {}'.format(thread.day_count))
        print('Last Time: {}'.format(thread.last_time))
        print('Max Oneday: {}'.format(thread.max_oneday))
        print()
    
    def output_file(self):
        with open('result_facebook.txt', 'w') as file:
            file.write(dumps(self.result, ensure_ascii=False))
    
    def run(self):
        self.make_list()
        for index, file_name in enumerate(self.file_list):
            if index%100 == 0:
                print("[INDEX] {}".format(index))
            self.count_messages(file_name)
        self.output_file()
        
    
if __name__ == '__main__':
    fb_counter = FacebookCounter(directory='/Users/alex/Downloads/facebook-cowbonlin/messages/')
    fb_counter.run()
    