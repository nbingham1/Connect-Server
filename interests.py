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
    total = 0;
    for interest in interests:
        for category in interest.keys():
            total += int(interest[category])
    for interest in interests:
        for category in interest.keys():
            cur.execute("select * from interests where user=%s and interest=%s", (long(form['user'].value), category))
            results = cur.fetchall()
            if len(results) > 0:
                for category in interest.keys():
                    cur.execute("update interests set count=%s, frequency=%s where user=%s and interest=%s", (interest[category], float(interest[category])/total, long(form['user'].value), category))
                con.commit()
                print "interests updated"
            else:
                for category in interest.keys():
                    cur.execute("insert into interests (user, interest, count, frequency) values (%s, %s, %s, %s)", (long(form['user'].value), category, interest[category], float(interest[category])/total))
		con.commit()
                print "interests added"
