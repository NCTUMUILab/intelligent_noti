from ContactLog.LogParser import FacebookJSONFilesFinder, FacebookLogParser, LineLogParser
from requests import get
from os import makedirs, path
from tkinter import Tk, filedialog

def gui_get_path(choose_type):
    window = Tk()
    window.withdraw()
    if choose_type == 'd':
        print("\tChoose the facebook backup directory. eg: /Users/alex/Downloads/messages")
        path = filedialog.askdirectory()
        window.update()
        return path
    elif choose_type == 'f':
        print("\tChoose line backup files")
        path_tuple = filedialog.askopenfilenames()
        window.update()
        return path_tuple
    raise ValueError


def get_userinfo_from_server():
    user_id = input("Enter user id: ")
    request = get("http://who.nctu.me:8000//contact/getJson?user_id=" + user_id)
    name = request.json()['name']
    fb_list = request.json()['fb_list']
    line_list = request.json()['line_list']
    if not path.exists("../userdata/{}".format(name)):
        makedirs("../userdata/{}".format(name))
    return name, fb_list, line_list


def get_facebook_log(username, fb_list):
    print("{:=^60}".format(" FACEBOOK STAGE START "))
    print("\tFacebook contacts:", fb_list)
    fb_homedir_path = gui_get_path('d')
    finder = FacebookJSONFilesFinder(fb_list, fb_homedir_path)
    print("COMPLETED FINDING JSON FILES. START PARSING")
    file_path_list = finder.export()
    for file_path in file_path_list:
        parser = FacebookLogParser(file_path)
        with open("../userdata/{}/fb-{}.json".format(username, parser.sender_name), 'w') as export_file:
            export_file.write(parser.export())
    print("{:=^40}\n".format(" FACEBOOK STAGE COMPLETED "))
    


def get_line_log(username, line_list):
    print("\n\n{:=^60}".format(" LINE STAGE START "))
    contact_parsed_list = [ [contact_name, False] for contact_name in line_list  ]
    path_tuple = gui_get_path('f')
    for file_path in path_tuple:
        parser = LineLogParser(contact_parsed_list, file_path)
        with open("../userdata/{}/line-{}.json".format(username, parser.contact_name), 'w') as file:
            file.write(parser.export())
    print("{:=^60}".format(" LINE STAGE COMPLETED "))


if __name__ == '__main__':
    username, fb_list, line_list = get_userinfo_from_server()
    # get_facebook_log(username, fb_list)
    get_line_log(username, line_list)
    