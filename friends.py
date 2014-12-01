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
	print(results)

if 'user' in form and 'json' in form:
	print(form['json'].value)
	
	
	json_data = json.loads(form['json'].value)
		
