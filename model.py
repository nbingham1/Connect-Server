#!/usr/bin/python
import cgi, cgitb
import requests
import MySQLdb as db
import time
import datetime
from datetime import datetime
import json
import sys

def get_distance(lat1, long1, lat2, long2):
	degrees_to_radians = math.pi/180.0
	phi1 = (90.0 - lat1)*degrees_to_radians
	phi2 = (90.0 - lat2)*degrees_to_radians
	theta1 = long1*degrees_to_radians
	theta2 = long2*degrees_to_radians
	cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
	math.cos(phi1)*math.cos(phi2))
	arc = math.acos( cos )
	return arc*6378100

def model(con, cur, user_id):
	cur.execute("select id,lat,lon from users")
	results = cur.fetchall()
	users = []
	for result in results:
		users.append([result[0], result[1], result[2], 0])

	print(users)

		


	cur.execute("select * from places where end > %s", (int(time.time() - 60*60*24*7),))
	results = cur.fetchall()

	

	for i in range(0, len(results)):
		for user in users:
			if user[0] == results[i][0]:
				user[3] = i
				print user

	return

sys.stderr = sys.stdout

con = db.connect('localhost', 'connect', 'socialize', 'connect')
cur = con.cursor()

form = cgi.FieldStorage()

print("Content-type: text/plain\r\n")
model(con, cur, form['user'].value)
