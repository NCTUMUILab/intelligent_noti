from .get_facebook import ThreadInfo
from random import randint
from datetime import datetime

contacts_test = []

for i in range(30):
	contact = ThreadInfo()
	
	contact.name = "Name{}".format(i),
	contact.is_group = True if i%2==0 else False,
	contact.msg_count = randint(0,600),
	contact.day_count = randint(0,30),
	contact.file_count = randint(0,10),
	contact.image_count = randint(1,10),
	contact.first_talk = datetime.now().strftime("%Y/%m/%d %H:%M"),
	contact.last_talk =  datetime.now().strftime("%Y/%m/%d %H:%M"),
	contact.last_msg = "test msg" 
	
	contacts_test.append(contact)
