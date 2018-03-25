from bs4 import BeautifulSoup
from json import dumps
from re import match
from datetime import datetime


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


class Message:
	def __init__(self):
		self.sender = None
		self.time = None
		self.raw = None
		self.others = None
	
	def __repr__(self):
		return "Message {}\n\tNAME: {}\n\tTIME: {}\n\tRAW : {}\n\tOTHE: {}".format(id(self), self.sender, self.time, self.raw, self.others)
	
	def clear(self):
		self.time = None
		self.raw = None
		self.others = None
	
	def dict(self):
		result = {'sender': self.sender,
			'time': self.time,
			'raw': self.raw,
			'others': self.others }
		return result


class FacebookLogParser: # similar as Thread
	def __init__(self, soup):
		self.soup = soup
		self.current_message = None
		self.result_list = []
		self._parse_page()
	
	def _parse_page(self):
		for child in self.soup.find('div', class_='thread').children:
			# meta data
			if child.name == 'div' and 'message' in child['class']:
				self.current_message = Message()
				self.current_message.sender = child.div.contents[0].text
				self.current_message.time = child.div.contents[1].text
			# content
			elif child.name == 'p':
				# not message (others)
				if child.p:
					# file
					if child.p.a:
						self.current_message.others = 'file'
					# image or sticker
					elif child.p.img:
						# stickers
						if 'stickers' in child.p.img['src']:
							self.current_message.others = 'stickers'
						# photo
						elif 'photo' in child.p.img['src']:
							self.current_message.others = 'photo'
						# gif
						elif 'gif' in child.p.img['src']:
							self.current_message.others = 'gif'
				# message
				else:
					encrypt_str = ""
					for char in child.text:
						if '\u4e00' <= char <= '\u9fff':
							encrypt_str += 'C'
						elif ('\u0041' <= char <= '\u005a') or ('\u0061' <= char <= '\u007a'):
							encrypt_str += 'E'
						elif '\u0030' <= char <= '\u0039':
							encrypt_str += 'D'
						else:
							encrypt_str += char
					self.current_message.raw = encrypt_str
				self.result_list.append(self.current_message.dict())
	
	def export(self):
		return dumps(self.result_list)
		

class LineLogParser:
	def __init__(self, file_path):
		self.file_path = file_path
		self.current_message = Message()
		self.current_datetime = datetime(2000, 1, 1)
		self.result_list = []
		self._parse_file()
		
	def _parse_file(self):
		with open(self.file_path) as file:
			for line in file:
				line = line.replace('\n', '')
				print("'"+line+"'")
				self._check_date(line)
				self._check_content(line)
				input()
	
	def _check_date(self, line):
		if match('\d{4}\/\d{2}\/\d{2}\(\S{2}\)', line):
			date_str = line[:-4]
			year, month, day = [ int(i) for i in date_str.split('/') ]
			self.current_datetime = self.current_datetime.replace(year=year, month=month, day=day)
			print('time:', self.current_datetime)
	
	
	def _check_content(self, line):
		if match('\d{2}:\d{2}\s', line):
			time_str, sender, raw = line.split('\t')
			hour, minute = [ int(i) for i in time_str.split(':') ]
			self.current_datetime = self.current_datetime.replace(hour=hour, minute=minute)
			self._update_message(sender, raw)
			
	
	def _update_message(self, sender, raw):
		self.current_message.clear()
		self.current_message.sender = sender
		self.current_message.raw = encrpyt_raw_text(raw)
		self.current_message.time = self.current_datetime.strftime("%y/%m/%d %H:%M")
		self.result_list.append(self.current_message.dict())
		print(self.current_message)
		
	
	def export(self):
		pass