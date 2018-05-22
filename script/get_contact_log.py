from ContactLog.LogParser import FacebookJSONFilesFinder, FacebookLogParser, LineLogParser
from requests import get
from os import makedirs, path
from tkinter import Tk, filedialog

def gui_get_path(choose_type):
    window = Tk()
    window.withdraw()
    if choose_type == 'd':
        print("Please choose the facebook backup directory.\n"
          "eg. /Users/alex/Downloads/messages")
        path = filedialog.askdirectory()
        window.update()
        return path
    elif choose_type == 'f':
        print("Please choose your Line backup files")
        path_tuple = filedialog.askopenfilenames()
        window.update()
        return path_tuple
    raise ValueError


def get_userinfo_from_server():
    user_id = input("Please enter User ID: ")
    request = get("http://who.nctu.me:8000//contact/getJson?user_id=" + user_id)
    name = request.json()['name']
    fb_list = request.json()['fb_list']
    line_list = request.json()['line_list']
    if not path.exists("../userdata/{}".format(name)):
        makedirs("../userdata/{}".format(name))
    return name, fb_list, line_list


def get_facebook_log(username, fb_list):
    print("FB CONTACT:", fb_list)
    fb_homedir_path = gui_get_path('d')
    finder = FacebookJSONFilesFinder(fb_list, fb_homedir_path)
    file_path_list = finder.export()
    for file_path in file_path_list:
        parser = FacebookLogParser(file_path)
        with open("../userdata/{}/fb-{}.json".format(username, parser.sender_name), 'w') as export_file:
            export_file.write(parser.export())
    print("Complete parsing facebook files\n")
    


def get_line_log(username, line_list):
    path_tuple = gui_get_path('f')
    for file_path in path_tuple:
        parser = LineLogParser(file_path)
        with open("../userdata/{}/line-{}.json".format(username, parser.export_file_name), 'w') as file:
            file.write(parser.export())
    print("Complete parsing line files")


if __name__ == '__main__':
    username, fb_list, line_list = get_userinfo_from_server()
    get_facebook_log(username, fb_list)
    get_line_log(username, line_list)
    