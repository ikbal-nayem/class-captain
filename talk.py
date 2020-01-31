import random

hello = ['hi', 'hello', 'hlo', 'hlw', 'hey', 'help']
r = ['Your requests is under processing.', 'We have your ID number.We will inform you', 'Contact your class captain to approve your requests.', 'when ever we will get any notice we will notify you.']
clients = []


class conversation:
	def __init__(self, senderID):
		self.senderID = senderID

	def official(self, message):
		self.message = message
		if self.senderID in clients:
			re = random.choice(r)
			return self.reply(re)

		elif '=' in message and 'id' in message.lower():
			clients.append(self.senderID)
			return self.reply('Thank you! I will inform you when class captain confarm your requests.;)')
		elif message.lower() in hello:
			return self.reply('Hi there! I am a campus bot which will inform you about your campus notice such as exam date, assignment etc.')
		else:
			return self.reply('You should to tell me your college ID number to get notification.\nFollow this format to send ID number\nid = <your_college_id>\nEx: id=123456')

	def reply(self, msg):
		return [{'id':[self.senderID], 'message':msg},
						{'id':['2221652174603040'], 'message':f'New message,\nID: {self.senderID}\nmsg: {self.message}'}]

