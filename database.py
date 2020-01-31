import sqlite3

class DB:

	def __init__(self):
		self.conn = sqlite3.connect('db/subscriber.db')
		# self.conn.execute('''create table if not exists class_room(id text PRIMARY KEY, class_id text, member_type text)''')


	def addMember(self, fb_id, classID=None, status='PENDING'):
		c = self.conn.cursor()
		c.execute('''INSERT INTO class_room VALUES(?,?,?)''',(fb_id, classID, status))
		self.conn.commit()
	
	
	def checkMember(self, fb_id):
		c = self.conn.cursor()
		c.execute('''SELECT member_type, class_id FROM class_room WHERE id=?''',(fb_id,))
		val = c.fetchone()
		if val:
			return val[0] if val[1] else 'NEW'
		self.addMember(fb_id)
		return 'WELCOME'


	def close(self):
		self.conn.close()


	def getReceiverList(self, specific=None, member='SUBSCRIBER'):
		c = self.conn.cursor()
		if specific:
			q = '''SELECT id FROM class_room WHERE class_id=?'''
			return [c.execute(q,(i,)).fetchone()[0] for i in specific]
		c.execute('''SELECT id FROM class_room WHERE member_type=?''',(member,))
		val = c.fetchall()
		return [i[0] for i in val] if val else None


	def getClassID(self, fb_id):
		c = self.conn.cursor()
		c.execute('''SELECT class_id FROM class_room WHERE id=?''',(fb_id,))
		return c.fetchone()[0]


	def update(self, classID, status='SUBSCRIBER'):
		c = self.conn.cursor()
		c.execute('''UPDATE class_room SET member_type=? WHERE class_id=?''',(status, classID))
		self.conn.commit()


	def updateID(self,fb_id, classID):
		c = self.conn.cursor()
		c.execute('''UPDATE class_room SET class_id=? WHERE id=?''',(classID, fb_id))
		self.conn.commit()


	def remove(self, classID):
		c = self.conn.cursor()
		c.execute('''DELETE FROM class_room WHERE class_id=? ''',(classID,))
		self.conn.commit()