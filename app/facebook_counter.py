from os import listdir
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from json import dumps

# class Thread(object):
#     def __init__(self):
        
class FacebookCounter(object):
    def __init__(self, directory):
        self.directory = directory
        self.soup = None
        self.file_list = []
        self.result = []
    
    def make_list(self):
        for file_name in listdir(self.directory):
            self.file_list.append(file_name)
        print('{} threads in total'.format( len(self.file_list) ))

    def count_messages(self, file_name):
        with open(self.directory+file_name, encoding='utf-8') as file:
            self.soup = BeautifulSoup(file.read(), 'html.parser')
        
        user_name = self.soup.find('title').get_text()[18:]
        if ',' in user_name or user_name == 'Facebook User' or not user_name:
            return
        p_tag_list = self.soup.find_all('p')
        time_list = self.soup.find_all('span', class_='meta')
        
        thirty_days_ago = datetime.now() - timedelta(days=30)
        msg_count = 0
        last_day = None
        day_count = 0

        for index, time in enumerate(time_list):
            msg_time = datetime.strptime(time.get_text()+"00", '%A, %B %d, %Y at %I:%M%p %Z%z').replace(tzinfo=None)
            tmp_last_day = datetime.strftime(msg_time, '%Y %m %d')
            if msg_time > thirty_days_ago:
                msg_count += 1
                if last_day != tmp_last_day:
                    day_count += 1
                    last_day = tmp_last_day
            else:
                break
        if msg_count > 0:
            print('Thread: {}'.format(file_name[:-5]))
            print('User: {}'.format(user_name))
            print('Message Count: {}'.format(msg_count))
            print('Day Count: {}\n'.format(day_count))
            thread_dict = { "user_name": user_name, 'msg_count': msg_count, 'day_count': day_count }
            self.result.append(thread_dict)
            
    def output(self):
        with open('result.txt', 'w') as file:
            file.write(dumps(self.result, ensure_ascii=False))
    
    def run(self):
        self.make_list()
        for index, file_name in enumerate(self.file_list):
            if index%100 == 0:
                print("[INDEX] {}".format(index))
            self.count_messages(file_name)
        self.output()
        # print('result: {}'.format(self.result))
        
    
if __name__ == '__main__':
    fb_counter = FacebookCounter(directory='/Users/alex/Downloads/facebook-cowbonlin/messages/')
    fb_counter.run()
    