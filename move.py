#!/usr/bin/python
import cgi, cgitb
import requests
import MySQLdb as db
import time
import datetime
from datetime import datetime
import json
import sys
from modelapi import *

sys.stderr = sys.stdout

con = db.connect('localhost', 'connect', 'socialize', 'connect')
cur = con.cursor()

form = cgi.FieldStorage()

print("Content-type: text/plain\r\n")

if 'user' in form and 'lat' in form and 'lon' in form:
	cur.execute("update users set lat=%s,lon=%s where id=%s", (form['lat'].value, form['lon'].value, form['user'].value,))
	con.commit()

	

