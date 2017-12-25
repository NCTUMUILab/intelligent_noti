from os import listdir
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from json import dumps
from re import finditer
from tkinter import Tk, filedialog


class Thread(object):
    def __init__(self, beautiful_soup, thread_no, language):
        self.soup = beautiful_soup
        self.thread_no = thread_no
        if language == "CH":
            self.user_name = self.soup.find('title').get_text()[10:]
        elif language == "EN":
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
        self.language = None
        self.time_format = {}
        
        self.time_format['CH'] = '%Y年%m月%d日 %H:%M %Z%z'
        self.time_format['EN'] = '%A, %B %d, %Y at %I:%M%p %Z%z'
    
    
    def make_list(self):
        for file_name in listdir(self.directory + "/messages/"):
            self.file_list.append(file_name)
        print('{} threads in total'.format( len(self.file_list) ))
    
    
    def set_language(self, index_soup):
        test_str = index_soup.find('li', class_='selected').get_text()
        if '\u4e00' <= test_str <='\u9fff':
            self.language = "CH"
        elif ('\u0041' <= test_str <= '\u005a') or ('\u0061' <= test_str <= '\u007a'):
            self.language = "EN"
        print('Language: {}'.format(self.language))
        
    
    def set_time_theshold(self, index_soup):
        download_time_raw = index_soup.find('div', class_='footer').get_text()
        if self.language == "CH":
            time_start_index = [ i.start() for i in finditer('在', download_time_raw) ][-1] + 2
            download_time_str = download_time_raw[time_start_index:-3]+"00"
        elif self.language == "EN":
            time_start_index = [ i.start() for i in finditer('on ', download_time_raw) ][-1] + 3
            download_time_str = download_time_raw[time_start_index:]+"00"
        
        download_time = datetime.strptime(download_time_str, self.time_format[self.language]).replace(tzinfo=None)
        self.time_threshold = download_time - timedelta(days=30)
        print("Time: {} ~ {}".format(self.time_threshold, download_time))
    
    
    def is_group(self, thread):
        if self.language == 'CH':
            try:
                participants = thread.soup.find('h3').next_sibling[14:]
            except TypeError as error:
               participants = thread.user_name
            if ',' in participants or not thread.user_name:
                return True
        elif self.language == 'EN':
            if ',' in thread.user_name or not thread.user_name:
                return True
        return False
        
    
    def count_messages(self, thread):        
        time_list = thread.soup.find_all('span', class_='meta') 
        last_day = None
        if time_list:
            last_time = datetime.strptime(time_list[0].get_text()+"00", self.time_format[self.language]).replace(tzinfo=None)
            thread.last_time = datetime.strftime(last_time, '%Y/%m/%d')
        
        tmp_max_oneday = 0
        for index, time in enumerate(time_list): # each message time
            msg_time = datetime.strptime(time.get_text()+"00", self.time_format[self.language]).replace(tzinfo=None)
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
        return thread
    
    
    def append_result(self, thread):
        self.result.append( { 
            "user_name": thread.user_name, 
            'msg_count': thread.msg_count, 
            'day_count': thread.day_count,
            'last_time': thread.last_time,
            'max_oneday': thread.max_oneday,
            'app': 'facebook' } )
          
            
    def print(self, thread):
        print('Thread: {}'.format(thread.thread_no))
        print('User: {}'.format(thread.user_name))
        print('Message Count: {}'.format(thread.msg_count))
        print('Day Count: {}'.format(thread.day_count))
        print('Last Time: {}'.format(thread.last_time))
        print('Max Oneday: {}'.format(thread.max_oneday))
        print()
    
    
    def run(self):
        with open(self.directory+"/index.htm") as file:
            index_soup = BeautifulSoup(file.read(), 'html.parser')
        
        self.set_language(index_soup)
        self.set_time_theshold(index_soup)
        self.make_list()
        
        for index, file_name in enumerate(self.file_list):
            file_path = self.directory + "/messages/" + file_name
            if index%100 == 0:
                print("[INDEX] {}".format(index))
            
            with open(file_path) as file:
                thread = Thread(BeautifulSoup(file.read(), 'html.parser'), file_name[:-5], self.language)
                
            if '_' in (file_path) or self.is_group(thread):
                continue
            else:
                thread = self.count_messages(thread)
                if thread.msg_count > 0:
                    self.print(thread)
                    self.append_result(thread)
        
        with open('result_facebook.txt', 'w') as file:
            file.write(dumps(self.result, ensure_ascii=False))
        
    
if __name__ == '__main__':
#     directory = input("\
# Please enter the path of directory.\n\
# eg. /Users/alex/Downloads/facebook-cowbonlin\n\
# Path: ")
    print("Please choose the facebook backup directory.\n"
          "eg. /Users/alex/Downloads/facebook-cowbonlin")
    Tk().withdraw()
    directory = filedialog.askdirectory(title="eg. /Users/alex/Downloads/facebook-cowbonlin")
    fb_counter = FacebookCounter(directory=directory)
    fb_counter.run()
    