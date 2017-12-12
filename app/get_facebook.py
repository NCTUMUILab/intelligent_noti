from fbchat import Client
from fbchat.models import ThreadType, FileAttachment, ImageAttachment
from time import time
from datetime import datetime, timedelta
import pickle
import logging
import requests
import json
import re


log = logging.getLogger("client")
log.setLevel(logging.INFO)

class ThreadInfo:
	def __init__(self):
		self.name = ""
		self.is_group = True
		self.msg_count = 0
		self.day_count = 0
		self.file_count = 0
		self.image_count = 0
		self.first_talk = ""
		self.last_talk = ""
		self.last_msg = ""


class fbMessenger:
	def __init__(self, username, password):
		self.client = Client(username, password) # facebook login

	def print(self, thread, index):
		print("{}.".format(index))
		print("thread name: {}".format(thread.name))
		print("type: {}".format("Group" if thread.is_group else "Single user"))
		print("msg count: {}".format(thread.msg_count))
		print("day count: {}".format(thread.day_count))
		print("file count: {}".format(thread.file_count))
		print("image count: {}".format(thread.image_count))
		print("first talk: {}".format(thread.first_talk))
		print("last talk: {}".format(thread.last_talk))
		print("last msg :'{}'\n".format(thread.last_msg))

	def get_messages(self):
		from_time = datetime.now() - timedelta(days=30) # msg records in previous 30 days
		threads = self.client.fetchThreadList(limit=20) # find 30 candidate contacts
		contact_list = []
		index = 1

		print("second try")
		for thread in threads:
			msgs = self.client.fetchThreadMessages(thread_id=str(thread.uid), limit=500)
			if thread.type == ThreadType.USER:

				thread_info = ThreadInfo()
				thread_info.name = thread.name
				thread_info.is_group = False if thread.type == ThreadType.USER else True
				thread_info.last_talk = datetime.fromtimestamp(int(msgs[0].timestamp) / 1000)
				thread_info.last_msg = msgs[0].text
				tem_day = None

				for msg in msgs:
					msg_time = datetime.fromtimestamp(int(msg.timestamp) / 1000)
					if from_time < msg_time:
						thread_info.msg_count += 1 if msg.text is not None else 0 # msg count
						thread_info.first_talk = datetime.fromtimestamp(int(msg.timestamp) / 1000) # first talk
						for atch in msg.attachments: # file count & image count
							if isinstance(atch, FileAttachment):
								thread_info.file_count += 1
							elif isinstance(atch, ImageAttachment):
								thread_info.image_count += 1
						if msg_time.day != tem_day: # dat count
							thread_info.day_count += 1
							tem_day = msg_time.day

				if thread_info.msg_count == 0:
					continue
				else:
					contact_list.append(thread_info)
					self.print(thread=thread_info, index=index)
				if index == 15: #################### number of candidate contacts #####################
					break
				else:
					index += 1

		return contact_list



if __name__ == "__main__":
	f = fbMessenger("", "")
	f.get_messages()
