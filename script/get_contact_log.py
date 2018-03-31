from ContactLog.LogParser import FacebookLogParser, LineLogParser
from ContactLog.FacebookContactSoupGenerator import FacebookContactSoupGenerator
from requests import get
from os import makedirs, path
from tkinter import Tk, filedialog

####################### user info #######################
email = input("Please enter your email: ")
request = get("http://localhost:5000/contact/getJson?email=" + email)
name = request.json()['name']
if not path.exists("../userdata/{}".format(name)):
	makedirs("../userdata/{}".format(name))

########################## line ##########################
### 1. get all the paths of backup files
print("Please choose your Line backup files")
window = Tk()
window.withdraw()
file_path_tuple = filedialog.askopenfilenames()
window.update()

### 2. parse and export to JSON file
for file_path in file_path_tuple:
	parser = LineLogParser(file_path)
	with open("../userdata/{}/{}".format(name, parser.export_file_name), 'w') as file:
		file.write(parser.export())
print("\tComplete parsing line files")

######################## facebook ########################

### 1. get facebook backup directory path
print("Please choose the facebook backup directory.\n"
      "eg. /Users/alex/Downloads/facebook-cowbonlin")
window = Tk()
window.withdraw()
directory_path = filedialog.askdirectory()
window.update()

### 2. get the list of facebook contact name
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

### delete unwanted file
while True:
	delete_index_number = input("Is any file that is not correct? Enter its index number: ")
	if not delete_index_number:
		break
	else:
		facebook_thread_list.pop(int(delete_index_number))
		print([ item['name'] for item in facebook_thread_list ])

while True:
	checkout_contact_name = input("Any one not in the list? Type his/her name: ")
	if not checkout_contact_name:
		break
	else:
		file_name_list = generator.name_to_file_dict.get(checkout_contact_name)
		if not file_name_list:
			print("\tSorry, Can't found it")
			print(generator.name_to_file_dict)
			continue
		else:
			print("\tFind:", file_name_list)
			index_number = int(input("Choose index number: "))
			soup = generator.get_file_soup(file_name_list[index_number])
			facebook_thread_list.append({ 'name':checkout_contact_name, 'soup':soup })
			print("\tAdd successfully!")
			

### 4. for each file: parse and export to json file
for thread in facebook_thread_list:
	print("\tParsing the chat history of", thread['name'], "...")
	file = open("../userdata/{}/{}.json".format(name, thread['name']), 'w')
	parser = FacebookLogParser(thread['soup'])
	file.write(parser.export())
print("FINISH")
