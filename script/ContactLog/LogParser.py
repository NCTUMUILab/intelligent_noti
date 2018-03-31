from bs4 import BeautifulSoup
from json import dumps
from re import match
from datetime import datetime, date


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


class Message:
    def __init__(self):
        self.sender = None
        self.time = None
        self.raw = None
        self.others = None
    
    def __repr__(self):
        return "Message {}\n\tNAME : {}\n\tTIME : {}\n\tRAW  : {}\n\tOTHER: {}".format(id(self), self.sender, self.time, self.raw, self.others)
    
    def clear(self):
        self.time = None
        self.raw = None
        self.others = None
    
    def dict(self):
        result = {'sender': self.sender,
            'time': self.time,
            'raw': self.raw,
            'others': self.others }
        return result


class FacebookLogParser: # similar as Thread
    def __init__(self, soup):
        self.soup = soup
        self.current_message = Message()
        self.result_list = []
        self._parse_page()
    
    def _parse_page(self):
        for child in self.soup.find('div', class_='thread').children:
            # meta data
            if child.name == 'div' and 'message' in child['class']:
                self.current_message.clear()
                self.current_message.sender = child.div.contents[0].text
                self.current_message.time = child.div.contents[1].text
            # content
            elif child.name == 'p':
                # not message (others)
                if child.p:
                    # file
                    if child.p.a:
                        self.current_message.others = 'file'
                    # image or sticker
                    elif child.p.img:
                        # stickers
                        if 'stickers' in child.p.img['src']:
                            self.current_message.others = 'stickers'
                        # photo
                        elif 'photo' in child.p.img['src']:
                            self.current_message.others = 'photo'
                        # gif
                        elif 'gif' in child.p.img['src']:
                            self.current_message.others = 'gif'
                # message
                else:
                    encrypt_str = ""
                    for char in child.text:
                        if '\u4e00' <= char <= '\u9fff':
                            encrypt_str += 'C'
                        elif ('\u0041' <= char <= '\u005a') or ('\u0061' <= char <= '\u007a'):
                            encrypt_str += 'E'
                        elif '\u0030' <= char <= '\u0039':
                            encrypt_str += 'D'
                        else:
                            encrypt_str += char
                    self.current_message.raw = encrypt_str
                self.result_list.append(self.current_message.dict())
    
    def export(self):
        return dumps(self.result_list)
        

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
            print("DATE:", self.current_date)
            return True
        elif match('^\d{4}\/\d{2}\/\d{2}\(\S{3}\)', line): # 3
            self.current_date = line[:-5]
            print("DATE:", self.current_date)
            return True
        elif match('^[A-Z][a-z]{2}, \d{2}\/\d{2}\/\d{4}', line):
            month_str, day_str, year_str = line[5:].split('/')
            self.current_date = "{}/{}/{}".format(year_str, month_str, day_str)
            print("DATE:", self.current_date)
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
        self.current_message.clear()
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