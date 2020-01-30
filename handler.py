import requests
from pymessenger import Bot
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

	def received(self, msg):
		if msg['object'] == 'page':
			for entry in msg['entry']:
				for message in entry['messaging']:
					self.senderID = message['sender']['id']
					self.pageID = message['recipient']['id']
					if message.get('message'):
						if Message.pageID == self.senderID:
							return
						self.bot.send_action(self.senderID, 'mark_seen')
						self.text = message['message']['text']
						self.mid = message['message']['mid']
						print(self.senderID+': '+self.text)
						self.bot.send_action(self.senderID, 'typing_on')
						msg = Process(self.senderID, self.text).start()
						self.send(msg)
						

	def send(self, msg):
		for m in msg:
			for reci in m['id']:
				self.bot.send_text_message(reci, m['message'])



class Process:

	def __init__(self, senderID, msg):
		self.senderID = senderID
		self.msg = msg


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


	def _admin(self):
		action = AdminPanel(self.senderID)
		if '*' in self.msg[0]:
			return action.post(self.msg[1:-1], to='all')
		elif '>' in self.msg:
			command, option = self.msg.split('>')
			if command.strip().lower() == 'add':
				return action.add(option.strip())
			elif command.strip().lower() == 'remove':
				return action.remove(option.strip())
			elif command.strip().lower() == 'see':
				return action.see(option.strip().upper())
		else:
			return action.conversation(self.msg)
	

	def _subscriber(self):
		db = DB()
		receiver = db.getReceiverList(member='ADMIN')
		cls_id = db.getClassID(self.senderID)
		db.close()
		info = INFO(self.senderID)
		msg = f'{info.firstName}({cls_id})-\n\n{self.msg}'
		return [{'id':receiver, 'message':msg}]


	def _pending(self):
		db = DB()
		receiver = db.getReceiverList(member='ADMIN')
		cls_id = db.getClassID(self.senderID)
		db.close()
		info = INFO(self.senderID)
		msg = f'{info.firstName}({cls_id})(panding user)-\n\n{self.msg}'
		return [{'id':receiver, 'message':msg},
						{'id':[self.senderID], 'message':'Your requests is still processing.\nPlease contact with your class captain.'}]
	

	def _new(self):
		if 'id' not in self.msg.lower():
			info = INFO(self.senderID)
			replay = f'Dear {info.lastName}, you have to write your class ID. (id > \'your_id\')'
			return [{'id': [self.senderID], 'message': replay},
							{'id': [self.senderID], 'message': ':)'}]
		if 'id' in self.msg.lower() and '>' in self.msg:
			cls_id = self.msg.split('>')[1].strip()
			db = DB()
			db.updateID(self.senderID, cls_id)
			receiver = db.getReceiverList(member='ADMIN')
			db.close()
			new_user = INFO(self.senderID)
			admin_msg = f'''{new_user.lastName} wants to be a member!
			Name : {new_user.firstName} {new_user.lastName}
			Class ID : {cls_id}'''
			return [{'id':[self.senderID], 'message':'Class captain permission required.\nI will let you know when you would get permission. ;)'},
							{'id':receiver, 'message':admin_msg}]


	def _welcome(self):
		if 'id' not in self.msg.lower():
			replay = f'Hello {INFO(self.senderID).firstName}!\nThis is your class assistent.\nI will notify you if you have any notice about exam, class test etc of your class\n:D'
			replay1 = 'All you need to do, tell me your id number in the following format:\n\nid > \'your_id_number\''
			return [{'id': [self.senderID], 'message': replay},
							{'id': [self.senderID], 'message': replay1}]
		return self._new()




class AdminPanel:
	def __init__(self, senderID):
		self.senderID = senderID

	
	def add(self, cls_id):
		db = DB()
		db.update(cls_id, status='SUBSCRIBER')
		fb_id = db.getReceiverList([cls_id])
		db.close()
		return [{'id':fb_id, 'messagee':'Your request has been approved. ;)'}]


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
		receiver = db.getReceiverList()
		db.close
		if receiver:
			return [{'id':receiver, 'message':msg},
							{'id':[self.senderID], 'message':'Message received.'}]
		return [{'id':[self.senderID], 'message':'No subscriber found.'}]


	def see(self, member='SUBSCRIBER'):
		db = DB()
		member_list = db.getReceiverList(member=member.upper())
		msg = f'{member} list:\n\n'
		if member_list:
			for l in member_list:
				info = INFO(l)
				cls_id = db.getClassID(l)
				msg += f'{info.firstName} {info.lastName} ({cls_id})\n'
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
