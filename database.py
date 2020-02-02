import pymysql
from conf import auth

class DB:

	def __init__(self):
		# self.conn = pymysql.connections.Connection(host='db4free.net', user='abid_captain', password='12345678', database='abid_captain')
		self.conn = pymysql.connections.Connection(host=auth.db_info['Server'], user=auth.db_info['Username'], password=auth.db_info['Password'], database=auth.db_info['Database'])
		# self.conn.execute('''create table if not exists class_room(id text PRIMARY KEY, class_id integer, member_type text)''')


	def addMember(self, fb_id, classID=None, status='PENDING'):
		c = self.conn.cursor()
		c.execute('''INSERT INTO class_room VALUES(%s,%s,%s)''',(fb_id, classID, status))
		self.conn.commit()


	def checkMember(self, fb_id):
		c = self.conn.cursor()
		c.execute('''SELECT member_type, class_id FROM class_room WHERE id=%s''',(fb_id,))
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
			c.execute('''SELECT id FROM class_room WHERE class_id=%s''', (specific,))
			return [c.fetchall()[0][0]]
		c.execute('''SELECT id FROM class_room WHERE member_type=%s''',(member,))
		val = c.fetchall()
		return [i[0] for i in val] if val else None


	def getClassID(self, fb_id):
		c = self.conn.cursor()
		c.execute('''SELECT class_id FROM class_room WHERE id=%s''',(fb_id,))
		return c.fetchone()[0]


	def update(self, classID, status='SUBSCRIBER'):
		c = self.conn.cursor()
		c.execute('''UPDATE class_room SET member_type=%s WHERE class_id=%s''',(status, classID))
		self.conn.commit()


	def updateID(self,fb_id, classID):
		c = self.conn.cursor()
		c.execute('''UPDATE class_room SET class_id=%s WHERE id=%s''',(classID, fb_id))
		self.conn.commit()


	def remove(self, classID):
		c = self.conn.cursor()
		c.execute('''DELETE FROM class_room WHERE class_id=%s ''',(classID,))
		self.conn.commit()




