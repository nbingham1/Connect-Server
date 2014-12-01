#!/usr/bin/python
import cgi, cgitb
import requests
import MySQLdb as db
import time
import datetime
from datetime import datetime
import json
import sys
import re


sys.stderr = sys.stdout

con = db.connect('localhost', 'connect', 'socialize', 'connect')
cur = con.cursor()

form = cgi.FieldStorage()

print("Content-type: text/plain\r\n")

if 'facebook' in form and 'user' in form and 'name' in form:
	cur.execute("update users set facebook=%s, name=%s where id=%s", (form['facebook'].value, form['name'].value, form['user'].value,))
	con.commit()
	cur.execute("select * from users")
	results = cur.fetchall()

if 'user' in form and 'json' in form:
	json_data = json.loads(form['json'].value)
	friends = json_data['data']
	ids = []
	query = "select facebook,id from users where facebook in ("
	for i in range(0, len(friends)-1):
		query += "%s,"
	query += "%s)"

	for friend in friends:
		ids.append(friend['id'])

	cur.execute(query, tuple(ids))
	results = cur.fetchall()
	
	for result in results:
		if long(form['user'].value) < long(result[1]):
			cur.execute("insert into friends (user1_id,user2_id,health,last_update) values (%s, %s, 0, 0) on duplicate key update user1_id=user1_id", (long(form['user'].value), long(result[1]),))
			con.commit()
		elif long(form['user'].value) != long(result[1]):
			cur.execute("insert into friends (user1_id,user2_id,health,last_update) values (%s, %s, 0, 0) on duplicate key update user1_id=user1_id", (long(result[1]), long(form['user'].value),))
			con.commit()
