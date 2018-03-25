from ContactLog.LogParser import FacebookLogParser, LineLogParser
from ContactLog.FacebookContactSoupGenerator import FacebookContactSoupGenerator
from requests import get
from os import mkdir
from tkinter import Tk, filedialog


########################## line ##########################
### 1. get backup files path
# window = Tk()
# window.withdraw()
# file_path = filedialog.askopenfilename()
# window.update()

### 2. parse and export to JSON file
parser = LineLogParser('/Volumes/COWBON_32G/david[LINE] 與張碧櫻的聊天.txt')


######################## facebook ########################
"""
### 1. get facebook backup directory path
print("Please choose the facebook backup directory.\n"
      "eg. /Users/alex/Downloads/facebook-cowbonlin")
window = Tk()
window.withdraw()
directory_path = filedialog.askdirectory()
window.update()

### 2. get the list of facebook contact name
email = input("Please enter your email: ")
request = get("http://localhost:5000/contact/getJson?email=" + email)
user_name = request.json()['name']
facebook_contact_list = []
for name_dict in request.json()['list']:
	if name_dict['facebook']:
		facebook_contact_list.append(name_dict['facebook'])
print(facebook_contact_list)

### 3. find out all html files of contact
generator = FacebookContactSoupGenerator(directory_path, facebook_contact_list)
facebook_thread_list = generator.find_all_soups()
if len(facebook_thread_list) == len(facebook_contact_list):
	print('Find all soups, start to parse')
else:
	print('Iterate all files, {} remains left'.format(abs(len(facebook_thread_list)-len(facebook_contact_list))))

### 4. for each file: parse and export to json file
mkdir(user_name)
for thread in thread_list:
	file = open("{}/{}.json".format(user_name, thread['name']), 'w')
	parser = FacebookLogParser(thread['soup'])
	file.write(parser.export())
print("FINISH")
"""