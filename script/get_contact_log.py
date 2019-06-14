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
    request = get("http://who.nctu.me:8081/contact/getJson?user_id=" + user_id)
    name = request.json()['name']
    fb_data = request.json()['fb_data']
    line_data = request.json()['line_data']
    if not path.exists("../userdata/{}".format(name)):
        makedirs("../userdata/{}".format(name))
    return name, fb_data, line_data


def get_facebook_log(username, fb_data):
    fb_list = [x for x in fb_data]
    print("{:=^60}".format(" FACEBOOK STAGE START "))
    print("\tFacebook contacts:", fb_list)
    fb_homedir_path = gui_get_path('d')
    finder = FacebookJSONFilesFinder(fb_list, fb_homedir_path)
    print("COMPLETED FINDING JSON FILES. START PARSING")
    file_path_list = finder.export()
    for file_path in file_path_list:
        parser = FacebookLogParser(file_path)
        if parser.sender_name in fb_data:
            contact_id = fb_data[parser.sender_name]
        else:
            contact_id = '?'
        with open("../userdata/{}/fb-{}-{}.json".format(username, contact_id, parser.sender_name), 'w') as export_file:
            export_file.write(parser.export())
    print("{:=^60}\n".format(" FACEBOOK STAGE COMPLETED "))


def get_line_log(username, line_data):
    line_list = [x for x in line_data]
    print("\n\n{:=^60}".format(" LINE STAGE START "))
    contact_parsed_list = [[contact_name, False] for contact_name in line_list]
    path_tuple = gui_get_path('f')
    for file_path in path_tuple:
        parser = LineLogParser(contact_parsed_list, file_path)
        fn = file_path.split('/')[-1]
        name = fn.replace('[LINE] 與', '').replace(
            '的聊天.txt', '').replace('[LINE] Chat with ', '').replace('.txt', '')
        if parser.contact_name in line_data:
            contact_id = line_data[parser.contact_name]
        else:
            contact_id = '?'
        with open("../userdata/{}/line-{}-{}.json".format(username, contact_id, name), 'w') as file:
            file.write(parser.export())
    print("{:=^60}".format(" LINE STAGE COMPLETED "))


if __name__ == '__main__':
    username, fb_data, line_data = get_userinfo_from_server()
    # get_facebook_log(username, fb_data)
    get_line_log(username, line_data)
