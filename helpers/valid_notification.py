def valid_notification(app, ticker, title, text, sub_text):
	if app in ('com.facebook.orca', 'com.facebook.mlite'):
		is_valid = True
		## if the notification is not what we want
		if "對話中有新訊息" in ticker or \
			"聊天大頭貼使用中" in title or \
			"傳送" in ticker or \
			"You missed a call from" in ticker or \
			"你錯過了" in ticker or \
			"sent" in ticker or \
			"reacted" in ticker or \
			"貼圖" in ticker or \
			"送出" in ticker or \
			"Wi-Fi" in ticker or \
			not ticker or \
			not title or \
			not text or \
			"：" in text or \
			":" in text:
			
			is_valid = False
			if text.startswith(title) and ":" in text:
				is_valid = True
		return is_valid
	
	elif app in ('jp.naver.line.android', 'com.linecorp.linelite'):
		is_valid = True
		## if the notification is not what we want
		if "You have a new message" in ticker or \
			" - " in title or \
			"邀請您加入" in text or \
			"LINE" in title or \
			"LINE" in ticker or \
			"LINE" in text or \
			"貼圖" in ticker or \
			"您有新訊息" in ticker or \
			"傳送了" in ticker or \
			"記事本" in ticker or \
			"已建立" in ticker or \
			"added a note" in ticker or \
			"sent" in ticker or \
			"語音訊息" in ticker or \
			"Wi-Fi" in ticker or \
			not ticker or \
			not title or \
			not text or \
			sub_text:
			
			is_valid = False
		return is_valid
	else:
		return False
			