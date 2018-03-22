from os import listdir
from bs4 import BeautifulSoup

class FacebookContactSoupGenerator:
	def __init__(self, directory_path, contact_list):
		self.directory_path = directory_path
		self.contact_list = contact_list
		self.soup_list = []
		self.language = self._get_language()


	def find_all_soups(self):
		for file_name in listdir(self.directory_path + "/messages/"):
			if '.html' in file_name and file_name[0] != '.':
				valid, soup, name = self._check_contact_in_list(file_name)
				if valid:
					self.soup_list.append({'name':name, 'soup': soup})
					if len(self.soup_list) == len(self.contact_list):
						break
		print('\tDONE!!')				
		return self.soup_list
	
	
	def _get_language(self):
		with open(self.directory_path+"/index.htm") as file:
			index_page_soup = BeautifulSoup(file.read(), 'html.parser')
			profile_str = index_page_soup.find('li', class_='selected').string
			if '\u4e00' <= profile_str[0] <= '\u9fff':
				return 'CH'
			elif ('\u0041' <= profile_str[0] <= '\u005a') or ('\u0061' <= profile_str[0] <= '\u007a'):
				return 'EN'
			else:
				raise UserWarning
	
	
	def _check_contact_in_list(self, file_name):
		""" check if contact of the given file is in self.contact_list.
		Args:
			file_name: the name of the file which user want to know its sender.
		
		Return:
			success: True if the sender of the file is in the list. False otherwise.
			soup: soup if in the list. None otherwise
			contact_name: name of the contact if in the list. None otherwise
		"""
		file_path = self.directory_path + "/messages/" + file_name
		with open(file_path) as file:
			soup = BeautifulSoup(file.read(), 'html.parser')
			if self.language == 'EN':
				contact_name = soup.title.string.replace("Conversation with ", "")
			elif self.language == 'CH':
				contact_name = soup.title.string.replace("與以下對象的對話： ", "")
			print("name:", contact_name)
			if contact_name in self.contact_list:
				print("\tFIND:", contact_name, file_name)
				return True, soup, contact_name
			else:
				return False, None, None