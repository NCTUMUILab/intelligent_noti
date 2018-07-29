from json import dumps, load
from re import match
from datetime import datetime, date
from os import listdir, path
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
            if path.isdir("{}/{}".format(self._homedir_path, subdir)) and path.exists(json_path):
                with open(json_path) as file:
                    try:
                        file_content_dict = load(file)
                    except UnicodeDecodeError:
                        print("\t\tJSON_LOAD_ERR:", json_path)
                        continue
                try:
                    contact_name = to_unicode(file_content_dict['title'])
                    self._name_path_dict[contact_name] = json_path
                except KeyError:
                    continue
    
    def _find_dirs(self, contact_list):
        remain_contact_set = set(contact_list)
        for contact_name in contact_list:
            if contact_name in self._name_path_dict:
                self._target_dir_list.append(self._name_path_dict[contact_name])
                remain_contact_set.discard(contact_name)
        
        if len(remain_contact_set):
            print("\tSOME CONTACTS CAN NOT BE FOUND:\n\tREMAINS: {}".format(remain_contact_set))
            while True:
                name = input("\tADD MORE CONTACT?: ")
                if not name:
                    break
                if name in self._name_path_dict:
                    self._target_dir_list.append(self._name_path_dict[name])
                    print("\t\tFOUND AND ADDED:", self._name_path_dict[name])
                else:
                    print("\t\t{} NOT FOUND".format(name))
        else:
            print("\tFound all contacts")
        
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
        return self._target_dir_list


class FacebookLogParser:
    def __init__(self, json_path):
        self._result_list = []
        with open(json_path) as file:
            ori_dict = load(file)
        self.sender_name = to_unicode(ori_dict['title'])
        print("\tParsing {}'s log ... ".format(self.sender_name))
        if not ori_dict.get('messages'):
            print("\n\t\tERROR: on messages in JSON")
            return
        # iterate each messages in original json file from facebook
        for msg_dict in ori_dict['messages']:
            self._result_list.append( self._convert_msg_dict(msg_dict) )
        print("\tCOMPLETE")
    
    def _convert_msg_dict(self, msg_dict):
        message = Message()
        try:
            message.time = msg_dict['timestamp']
        except KeyError:
            message.time = msg_dict['timestamp_ms']
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
        elif 'reactions' in msg_dict:
            message.others = "reaction"
        elif len(msg_dict) == 3:
            message.others = "empty"
        else:
            print("OTHER TYPE OF MESSAGE:", msg_dict)
        
        return message.dict()
    
    def export(self):
        return dumps(self._result_list)


class LineLogParser:
    def __init__(self, contact_parsed_list, file_path):
        self.file_path = file_path
        self.import_file_name = file_path.split('/')[-1]
        self.current_date = "2000/1/1"
        self._result_list = []
        self._special_case = False
        
        got_id, value = self._print_list_and_select_contact(self.import_file_name, contact_parsed_list)
        self.contact_name = contact_parsed_list[value][0] if got_id else value
        print("\t\tPARSING {}'S LOG ... ".format(self.contact_name))
        self._parse()
        print("\t\tCOMPLETE")    
    
    
    def _print_list_and_select_contact(self, file_name, contact_parsed_list):
        print("\n\tLine contacts:")
        for index, contact_parsed in enumerate(contact_parsed_list):
            print("\t\t[{:2d}] [{}]  {}".format(index, "COMPLETE" if contact_parsed[1] else " NOT YET", contact_parsed[0]))
        print("\tFile to parse: {}".format(file_name))
        contact_id_str = input("\tWhich contact is he/she?(enter the contact id, leave a blank if no match): ")
        if contact_id_str:
            try:
                contact_id = int(contact_id_str)
                contact_parsed_list[contact_id][1] = True
                return True, contact_id
            except ValueError:
                print("Oops, You should enter his/her contact id, not the others.")
        
        contact_name = input("\tWhat is the contact's name?: ")
        return False, contact_name
            
    
    
    def _parse(self):
        with open(self.file_path) as file:
            for line in file:
                line = line.replace('\n', '').replace('\ufeff', '') # Zero Width No-Break Space
                if self._check_date(line):
                    continue
                elif self._check_new_message(line):
                    continue
                elif self._check_others(line):
                    continue
                else:
                    continue
    
    
    def _check_date(self, line):
        ymd = match('^\d{4}\/\d{2}\/\d{2}', line) # 2018/04/23(週一), 2018/03/19（一）, 2018/04/23(Mon)
        if ymd:
            self.current_date = ymd.group(0)
            return True
        
        mdy = match('^[A-Z][a-z]{2}, \d{2}\/\d{2}\/\d{4}', line) # Thu, 04/23/2018
        if mdy:
            month_str, day_str, year_str = line[5:].split('/')
            self.current_date = "{}/{}/{}".format(year_str, month_str, day_str)
            return True
        
        ymd_dot =  match('^\d{4}.\d{2}.\d{2} ', line) # 2017.12.22 星期五
        if ymd_dot:
            self._special_case = True
            self.current_date = ymd_dot.group(0).replace('.', '/')
            return True
        
        return False
    
    
    def _check_new_message(self, line):
        if match('^\d{1,2}:\d{2}\t', line): # 3:12  sender  text
            try:
                tab_split_list = line.split('\t')
                time_str = tab_split_list[0]
                sender   = tab_split_list[1]
                raw = tab_split_list[2]
                self._append_new_message(time_str, sender, raw)
            except ValueError:
                print("4", line)
            return True
        
        elif match('^\d{2}:\d{2} [AP]M\t', line): # 01:22 PM
            try:
                time_str, sender, raw = line.split('\t')
                self._append_new_message(time_str, sender, raw)
            except ValueError:
                print("3", line)
                # pass
            return True
        
        elif match('^\S{2}\d{2}:\d{2}\t', line): #下午02:04    sender CCCCC
            try:
                time_str, sender, raw = line.split('\t')
                self._append_new_message(time_str, sender, raw)
            except ValueError: # 下午02:09    您已收回訊息
                print("2", line)
                # pass
            return True 
        
        elif self._special_case and match('^\d{2}:\d{2} ', line): # 01:22 Kevin Goodbye
            try:
                time_str, sender, raw = line.split(' ', 2)
                self._append_new_message(time_str, sender, raw)
            except ValueError:
                print("1", line)
                # pass
            return True
            
        else:
            return False
    
                
    def _check_others(self, line):
        if match('^\[LINE\] ', line) or match('^Chat history', line):
            return
        elif match('^儲存日期：', line) or match('Saved on: ', line):
            return
        elif line == '':
            return
        else: # cont message
            try:
                self._result_list[-1]['raw'] += '\n' + encrpyt_raw_text(line)
            except Exception as e:
                print("\t\tAPPEND MESSAGE ERROR:", line, e)
    
    
    def _append_new_message(self, time_str, sender, raw):
        new_message = Message()
        new_message.sender = sender
        new_message.time = self.current_date + ' ' + time_str
        if match('^\[\S+\]$', raw):
            new_message.others = raw.replace('[', '').replace(']', '')
        elif self._special_case and raw in ('圖片', '貼圖'):
            new_message.others = raw
        else:
            new_message.raw = encrpyt_raw_text(raw)
        self._result_list.append(new_message.dict())
    
    
    def export(self):
        return dumps(self._result_list)
    

if __name__ == '__main__':
    parser = LineLogParser('/Users/alex/Desktop/LINE TEXT/[LINE]江姿燕.txt')
    with open('/Users/alex/Desktop/testlinelog.json', 'w') as file:
        file.write(parser.export())