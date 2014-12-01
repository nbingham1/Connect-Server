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

if 'user' in form and 'json' in form:
	json_data = json.loads(form['json'].value)
	interests = json_data['data']
	# need a table called interests with ((long?) user_id, (varchar(64)?) interest) as composite primary key
	for interest in interests:
		cur.execute("insert into interests (user_id, interest) values (%s, %s)", (long(form['user'].value), interest['name']))
		con.commit()
	print "interests added"
