from bs4 import BeautifulSoup
from json import dumps, load
from re import match
from datetime import datetime, date
from os import listdir, path
from pypinyin import lazy_pinyin
from urllib.parse import unquote


def encrpyt_raw_text(raw_text):
    encrypt_str = ""
    for char in raw_text:
        if '\u4e00' <= char <= '\u9fff':
            encrypt_str += 'C'
        elif ('\u0041' <= char <= '\u005a') or ('\u0061' <= char <= '\u007a'):
            encrypt_str += 'E'
        elif '\u0030' <= char <= '\u0039':
            encrypt_str += 'D'
        else:
            encrypt_str += char
    return encrypt_str

def to_unicode(ori_str):
        url_format_str = ''
        for c in ori_str:
            url_format_str += '%{}'.format( format(ord(c), 'x') )
        return unquote(url_format_str)

class Message:
    def __init__(self):
        self.sender = None
        self.time = None
        self.raw = None
        self.others = None
    
    def __repr__(self):
        return "Message {}\n\tNAME : {}\n\tTIME : {}\n\tRAW  : {}\n\tOTHER: {}".format(id(self), self.sender, self.time, self.raw, self.others)
    
    def dict(self):
        return self.__dict__


class FacebookJSONFilesFinder:
    def __init__(self, contact_list, homedir_path):
        self._target_dir_list = []
        self._homedir_path = homedir_path
        self._msg_dir_list = listdir(homedir_path)
        self._name_path_dict = {}
        self._get_name_path_dict()
        self._find_dirs(contact_list)
        
    
    def _get_name_path_dict(self):
        for subdir in self._msg_dir_list:
            json_path = "{}/{}/message.json".format(self._homedir_path, subdir)
            if path.exists(json_path):
                with open(json_path) as file:
                    file_content_dict = load(file)
                try:
                    contact_name = to_unicode(file_content_dict['title'])
                    self._name_path_dict[contact_name] = json_path
                except KeyError:
                    print("NOTITLE:", subdir)
    
    
    def _find_dirs(self, contact_list):
        for contact_name in contact_list:
            if contact_name in self._name_path_dict:
                self._target_dir_list.append(self._name_path_dict[contact_name])
        
        if len(self._target_dir_list) != len(contact_list):
            print("NOTFOUND", self._target_dir_list, contact_list)
            while True:
                name = input("ADD MORE CONTACT?: ")
                if not name:
                    break
                if name in self._name_path_dict:
                    self._target_dir_list.append(self._name_path_dict[name])
                    print("FOUND AND ADDED:", self._name_path_dict[name])
        else:
            print("FOUND ALL CONTACTS:", self._target_dir_list)
        # contact_pinyin_list = [ ''.join(lazy_pinyin(name)).lower().replace(' ', '') for name in contact_list ]
        # contact_dir_found = [ False for i in contact_list ]
        # for each_dir_name in self._msg_dir_list:
        #     for i, pinyin in enumerate(contact_pinyin_list):
        #         pinyin += '_'
        #         if each_dir_name.find(pinyin) == 0:
        #             self._target_dir_list.append(each_dir_name)
        #             contact_dir_found[i] = True 
        
        # if len(self._target_dir_list) != len(contact_list):
        #     for pinyin, name, found in zip(contact_pinyin_list, contact_list, contact_dir_found):
        #         if not found:
        #             print("\t{} not found: {}".format(name, pinyin))
        
    def search(self, pinyin):
        search_result = []
        for each_dir_name in self._msg_dir_list:
            if pinyin in each_dir_name:
                print("\tFOUND:{} {}".format(len(search_result), each_dir_name))
                search_result.append(each_dir_name)
        if search_result:
            index_str = input("Which one?(enter index): ")
            if not index_str:
                return
            else:
                index = int(index_str)
                self._target_dir_list.append(search_result[index])
                print("\tADD {} SUCCESSFULLY".format(search_result[index]))
        else:
            print("\tNOT FOUND")
            
    
    def export(self):
        # return [ "{}/{}/message.json".format(self._homedir_path, wanted_dir) for wanted_dir in self._target_dir_list ]
        return self._target_dir_list


class FacebookLogParser:
    def __init__(self, json_path):
        self._result_list = []
        with open(json_path) as file:
            ori_dict = load(file)
        self.sender_name = to_unicode(ori_dict['title'])
        for msg_dict in ori_dict['messages']:
            self._result_list.append( self._convert_msg_dict(msg_dict) )
    
    def _convert_msg_dict(self, msg_dict):
        message = Message()
        message.time = msg_dict['timestamp']
        message.sender = to_unicode(msg_dict['sender_name'])
        if 'content' in msg_dict:
            message.raw = encrpyt_raw_text(to_unicode(msg_dict['content']))
        elif 'sticker' in msg_dict:
            message.others = "sticker"
        elif 'files' in msg_dict:
            message.others = "file"
        elif 'videos' in msg_dict:
            message.others = "video"
        elif 'photos' in msg_dict:
            message.others = "photo"
        elif 'gifs' in msg_dict:
            message.others = "gif"
        elif 'share' in msg_dict:
            message.others = "share"
        elif 'plan' in msg_dict:
            message.others = "plan"
        elif 'audio_files' in msg_dict:
            message.others = "audio"
        elif len(msg_dict) == 3:
            message.others = "empty"
        else:
            print("Attention:", msg_dict)
        
        return message.dict()
    
    def export(self):
        return dumps(self._result_list)


class LineLogParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.export_file_name = None
        self.current_message = Message()
        self.current_date = "2000/1/1"
        self.result_list = []
        self._parse_file()
      
        
    def _parse_file(self):
        with open(self.file_path) as file:
            for line in file:
                line = line.replace('\n', '')
                is_date = self._check_date(line)
                if not is_date:
                    is_content = self._check_new_content(line)
                    if not is_content:
                        self._check_cont_content(line)
    
    
    def _check_date(self, line):
        if match('^\d{4}\/\d{2}\/\d{2}\(\S{2}\)', line): # 3
            self.current_date = line[:-4]
            print("DATE1:", self.current_date)
            return True
        elif match('^\d{4}\/\d{2}\/\d{2}\(\S{3}\)', line): # 3
            self.current_date = line[:-5]
            print("DATE2:", self.current_date)
            return True
        elif match('^[A-Z][a-z]{2}, \d{2}\/\d{2}\/\d{4}', line):
            month_str, day_str, year_str = line[5:].split('/')
            self.current_date = "{}/{}/{}".format(year_str, month_str, day_str)
            print("DATE3:", self.current_date)
            return True
        else:
            return False
    
    
    def _check_new_content(self, line):
        if match('^\d{1,2}:\d{2}\t', line):
            time_str, sender, raw = line.split('\t')
        elif match('^\d{2}:\d{2} [AP]M\t', line):
            try:
                time_str, sender, raw = line.split('\t')
            except ValueError:
                print("!!! ISSUE:'{}' !!!".format(line))
                return True
        else:
            return False
        
        # packaging message
        self.current_message = Message()
        self.current_message.sender = sender
        self.current_message.time = self.current_date + ' ' + time_str
        if match('^\[\S+\]$', raw):
            self.current_message.others = raw.replace('[', '').replace(']', '')
        else:
            self.current_message.raw = encrpyt_raw_text(raw)
        
        self.result_list.append(self.current_message.dict())
        return True
            
            
    def _check_cont_content(self, line):
        if '[LINE] ' in line or 'Chat history' in line:
            self.export_file_name = line
        elif match('^儲存日期：', line) or match('Saved on: ', line):
            pass
        elif line == '':
            pass
        else:
            try:
                self.result_list[-1]['raw'] += '\n' + encrpyt_raw_text(line)
            except:
                print("ERROR:", line)
    
    
    def export(self):
        return dumps(self.result_list)