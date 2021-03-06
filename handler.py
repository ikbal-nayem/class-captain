import requests
import time
from pymessenger import Bot
import random
from conf import auth
from database import DB



class Message:
	pageID = '107595967464218'

	def __init__(self):
		self.bot = Bot(auth.BOT_TOKEN)
		self.pageID = None
		self.senderID = None
		self.text = None
		self.mid = None
		self.img_url = None

	def received(self, data):
		if data['object'] == 'page':
			for entry in data['entry']:
				for message in entry['messaging']:
					self.senderID = message['sender']['id']
					self.pageID = message['recipient']['id']
					if message.get('message'):
						self.mid = message['message']['mid']
						if Message.pageID == self.senderID:
							return
						self.bot.send_action(self.senderID, 'mark_seen')
						if message['message'].get('text'):
							self.text = message['message']['text']
							print(self.senderID+': '+self.text)
							self.bot.send_action(self.senderID, 'typing_on')
							try:
								reply = Process(self.senderID, msg=self.text).start()
								self.send(reply)
							except Exception as e:
								print(str(e))
						elif message['message'].get('attachments'):
							for attachment in message['message']['attachments']:
								if attachment['payload'].get('url'):
									self.img_url = attachment['payload']['url']
									reply = Process(self.senderID).image(self.img_url)
									self.send(reply)


	def send(self, msg):
		for m in msg:
			print(f"Sending message to {len(m['id'])} peoples.")
			for i, reci in enumerate(m['id']):
				if m.get('message'):
					mg = m['message']
					self.bot.send_text_message(reci, mg)
				if m.get('img'):
					ig = m['img']
					self.bot.send_image_url(reci, ig)



class Process:

	def __init__(self, senderID, msg=''):
		self.senderID = senderID
		self.msg = msg
		self.url = None


	def start(self):
		sender_type = DB().checkMember(self.senderID)
		if sender_type == 'ADMIN':
			return self._admin()
		elif sender_type == 'SUBSCRIBER':
			return self._subscriber()
		elif sender_type == 'PENDING':
			return self._pending()
		elif sender_type == 'NEW':
			return self._new()
		elif sender_type == 'WELCOME':
			return self._welcome()
	

	def image(self, link):
		db = DB()
		sender_type = db.checkMember(self.senderID)
		if sender_type == 'ADMIN':
			subs = db.getReceiverList(member='SUBSCRIBER')
			admin = db.getReceiverList(member='ADMIN')
			del admin[admin.index(self.senderID)]
			db.close()
			return [{'id':subs, 'img':link},
							{'id':[self.senderID], 'message':'Photo sent ;)'},
							{'id':admin, 'message':INFO(self.senderID).firstName+'(ADMIN)-'},
							{'id':admin, 'img':link}]
		elif sender_type == 'SUBSCRIBER':
			admin = db.getReceiverList(member='ADMIN')
			cls_id = db.getClassID(self.senderID)
			db.close()
			return [{'id':admin, 'message':INFO(self.senderID).firstName+f'({cls_id})-'},
							{'id':admin, 'img':link}]


	def _admin(self):
		action = AdminPanel(self.senderID)
		if '*' in self.msg[0]:
			return action.post(self.msg[1:], to='all')
		elif '>' in self.msg:
			command, option = self.msg.split('>')
			if command.strip().lower() == 'add':
				return action.add(option.strip())
			elif command.strip().lower() == 'remove':
				return action.remove(option.strip())
			elif command.strip().lower() == 'see':
				return action.see(option.strip().upper())
			else:
				try:
					int(command.strip())
					db = DB()
					checkID = db.getReceiverList(specific=command.strip())
					db.close()
					return [{'id':checkID, 'message':option.strip()}]
				except Exception as e:
					db.close()
					if e == 'tuple index out of range':
						return [{'id':[self.senderID], 'message':'Wrong ID'}]
					return [{'id':[self.senderID], 'message':'Command error. :('}]
		else:
			return action.conversation(self.msg)
	

	def _subscriber(self):
		db = DB()
		receiver = db.getReceiverList(member='ADMIN')
		cls_id = db.getClassID(self.senderID)
		db.close()
		info = INFO(self.senderID)
		msg = f'{info.firstName}({cls_id})-\n{self.msg}'
		return [{'id':receiver, 'message':msg}]


	def _pending(self):
		r = ['Your requests is under processing.', 'We have your ID number.We will inform you', 'Contact your class captain to approve your requests.', 'Your requests is still processing.\nPlease contact with your class captain.']
		db = DB()
		receiver = db.getReceiverList(member='ADMIN')
		cls_id = db.getClassID(self.senderID)
		db.close()
		info = INFO(self.senderID)
		msg = f'{info.firstName}({cls_id})(panding)-\n{self.msg}'
		return [{'id':receiver, 'message':msg},
						{'id':[self.senderID], 'message':random.choice(r)}]
	

	def _new(self):
		if 'id' not in self.msg.lower():
			info = INFO(self.senderID)
			replay = f'Dear {info.lastName},\nYou have to write your class ID. (EX: id = 12345)'
			return [{'id': [self.senderID], 'message': replay},
							{'id': [self.senderID], 'message': ':)'}]
		if 'id' in self.msg.lower() and '=' in self.msg:
			cls_id = self.msg.split('=')[1].strip()
			db = DB()
			db.updateID(self.senderID, cls_id)
			receiver = db.getReceiverList(member='ADMIN')
			db.close()
			new_user = INFO(self.senderID)
			admin_msg = f'{new_user.firstName} wants to be a member!\nName : {new_user.firstName} {new_user.lastName}\nID number : {cls_id}'
			return [{'id':[self.senderID], 'message':'Class captain permission required.\nI will let you know when you would get permission. ;)'},
							{'id':receiver, 'message':admin_msg},
							{'id':receiver, 'img':new_user.profilePic}]


	def _welcome(self):
		if 'id' not in self.msg.lower():
			replay = f'Hello {INFO(self.senderID).firstName}!\nThis is your class assistent.\nI will notify you if you have any notice about exam, assignment etc from your class\n:D'
			replay1 = 'All you need to do, tell me your id number in the following format:\n\nid = <your_class_id>\nEX: id=12345'
			return [{'id': [self.senderID], 'message': replay},
							{'id': [self.senderID], 'message': replay1}]
		return self._new()


#####				ADMIN PANAL

class AdminPanel:
	def __init__(self, senderID):
		self.senderID = senderID

	
	def add(self, cls_id):
		db = DB()
		db.update(cls_id, status='SUBSCRIBER')
		fb_id = db.getReceiverList(specific=cls_id)
		admin = db.getReceiverList(member='ADMIN')
		db.close()
		return [{'id':fb_id, 'messagee':'Your request has been approved. ;)\nNow you will get all notice from the class captain.'},
						{'id':admin, 'message':f'ID {cls_id} has been added to the subscriber list.'}]


	def conversation(self, msg):
		feedback = None
		welcome = ['hi', 'hlw', 'hello', 'hey', 'hlo']
		tnx = ['thank you', 'tnx', 'thnk u', 'tnk u', 'thank u']
		if msg in welcome:
			feedback = msg+' '+INFO(self.senderID).firstName
		elif msg in tnx:
			feedback = 'Welcome '+INFO(self.senderID).lastName
		else:
			feedback = 'To send a notice type \'*\' before your message.'
		return [{'id':[self.senderID], 'message':feedback}]

	
	def post(self, msg, to=None):
		db = DB()
		if to=='all':
			subs = db.getReceiverList(member='SUBSCRIBER')
			admin = db.getReceiverList(member='ADMIN')
			del admin[admin.index(self.senderID)]
			info = INFO(self.senderID)
		db.close
		if subs:
			return [{'id':subs, 'message':msg},
							{'id':[self.senderID], 'message':'Message sent.'},
							{'id':admin, 'message':f'{info.firstName}(ADMIN) - \n'+msg}]
		return [{'id':[self.senderID], 'message':'No subscriber found.'}]


	def see(self, member='SUBSCRIBER'):
		db = DB()
		member_list = db.getReceiverList(member=member.upper())
		msg = f'{member} list:\n\n'
		if member_list:
			for i,l in enumerate(member_list):
				info = INFO(l)
				cls_id = db.getClassID(l)
				msg += f'{i+1}. {info.firstName} {info.lastName} ({cls_id})\n'
			db.close()
		else:
			msg = f'No {member} found!'
		return [{'id':[self.senderID], 'message':msg}]

	
	def remove(self, cls_id):
		db = DB()
		db.remove(cls_id)
		db.close()
		return [{'id':[self.senderID], 'message':f'ID {cls_id} has been removed from subscriber list.'}]


	



class INFO:

	def __init__(self, id):
		self.firstName = None
		self.lastName = None
		self.profilePic = None
		self.url = 'https://graph.facebook.com/v2.6/{}/?access_token={}'.format(id, auth.BOT_TOKEN)
		self._getUserInfo()

	def _getUserInfo(self):
		js = requests.get(self.url).json()
		if js.get('first_name'):
			self.firstName = js['first_name']
			self.lastName = js['last_name']
			self.profilePic = js['profile_pic']
