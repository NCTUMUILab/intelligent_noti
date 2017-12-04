from get_facebook import ThreadInfo
from random import randint
from datetime import datetime

contacts_test = []

for i in range(30):
	contact = ThreadInfo(
		name = "Name{}".format(i),
		is_group = True if i%2==0 else False,
		msg_count = randint(0,600),
		day_count = randint(0,30),
		file_count = randint(0,10),
		image_count = randint(1,10),
		first_talk = datetime.now().strftime("%Y/%m/%d %H:%M"),
		last_talk =  datetime.now().strftime("%Y/%m/%d %H:%M"),
		last_msg = "test msg" )
	contacts_test.append(contact)
