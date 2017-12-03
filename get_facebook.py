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
	def __init__(self, name, type, msg_count, day_count, file_count, image_count, first_talk, last_talk, last_msg):
		self.name = name
		self.type = type
		self.msg_count = msg_count
		self.day_count = day_count
		self.file_count = file_count
		self.image_count = image_count
		self.first_talk = first_talk
		self.last_talk = last_talk
		self.last_msg = last_msg
	

class fbMessenger:
	def __init__(self, username, password):
		self.client = None
		self.login(username, password)

	def login(self, username, password):
		client = Client(username, password)
		self.client = client

	def get_messages(self):
		from_time = datetime.now() - timedelta(days=30) # msg records in previous 30 days
		threads = self.client.fetchThreadList(limit=10) # find 30 candidate contacts 
		thread_index = 0
		contact_list = []
		
		for thread in threads:
			msgs = self.client.fetchThreadMessages(thread_id=str(thread.uid), limit=500)
			msg_count = 0
			last_talk = datetime.fromtimestamp(int(msgs[0].timestamp) / 1000)
			first_talk = datetime.fromtimestamp(int(msgs[0].timestamp) / 1000)
			thread_index += 1
			day_count = 0
			tem_day = None
			file_count = 0
			image_count = 0
			
			for msg in msgs:
				msg_time = datetime.fromtimestamp(int(msg.timestamp) / 1000)
				for atch in msg.attachments:
					if isinstance(atch, FileAttachment):
						file_count += 1
					elif isinstance(atch, ImageAttachment):
						image_count += 1 
				if from_time < msg_time:
					msg_count += 1 if msg.text is not None else 0
					first_talk = datetime.fromtimestamp(int(msg.timestamp) / 1000)
					if msg_time.day != tem_day:
						day_count += 1
						tem_day = msg_time.day
			
			print("{}.".format(thread_index))
			print("thread name: {}".format(thread.name))
			print("type: {}".format("Single user" if thread.type == ThreadType.USER else "Group"))
			print("msg count: {}".format(msg_count))
			print("day count: {}".format(day_count))
			print("file count: {}".format(file_count))
			print("image count: {}".format(image_count))
			print("first talk: {}".format(first_talk.strftime("%Y/%m/%d %H:%M")))
			print("last talk: {}".format(last_talk.strftime("%Y/%m/%d %H:%M")))
			print("last msg :'{}'".format(msgs[0].text))
			print()
			
			thread_info = ThreadInfo(
				thread.name, 
				"Single user" if thread.type == ThreadType.USER else "Group",
				msg_count,
				day_count,
				file_count,
				image_count,
				first_talk.strftime("%Y/%m/%d %H:%M"),
				last_talk.strftime("%Y/%m/%d %H:%M"),
				msgs[0].text)
			
			contact_list.append(thread_info)
		return contact_list



if __name__ == "__main__":
	f = fbMessenger("", "")
	f.get_messages()
