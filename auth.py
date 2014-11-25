#!/usr/bin/python
import cgi, cgitb
import requests
import MySQLdb as db
import time
import datetime
from datetime import datetime
import json
import sys

sys.stderr = sys.stdout

con = db.connect('localhost', 'connect', 'socialize', 'connect')
cur = con.cursor()

form = cgi.FieldStorage()

def totimestamp(dt, epoch=datetime(1970,1,1)):
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 1e6 

def check_location_and_add(lid, lat, lon):
	cur.execute("select id,lat,lon from locations where id=%s", (lid,))
        results = cur.fetchall()
	if len(results) == 0:
		cur.execute("insert into locations (id,lat,lon) values (%s, %s, %s)", (lid, lat, lon,))
		con.commit()
	return

def check_place_and_add(user_id, location_id, start, end, place_name):
	cur.execute("select user_id,location_id,start,end,place from places where location_id=%s and start=%s and end=%s", (location_id,start,end,))
	results = cur.fetchall()
	if len(results) == 0:
		cur.execute("insert into places (user_id, location_id, start, end, place) values (%s, %s, %s, %s, %s)", (user_id, location_id, start, end, place_name,))
		con.commit()
	return

print("Content-type: text/plain\r\n\r\n")
if 'code' in form or 'refresh_token' in form:
	url='https://api.moves-app.com/oauth/v1/access_token'
	payload={}
	if 'code' in form:
		payload = { 'grant_type' : 'authorization_code',
			    'code' : form['code'].value,
			    'client_id' : 'BHJJXLewp3VFBhgOY1T7NVlyXGsOtMF1',
			    'client_secret' : 'PnpXEjNU4xKiwp69q6pBTrva04Ez94arfCXvg9n3FxVwG5DQN7tUBnSKN7NFc5ch', 
			    'redirect_uri' : 'http://connect.sol-union.com/index.py' }
	elif 'refresh_token' in form:
	        payload = { 'grant_type' : 'refresh_token',
        	            'refresh_token' : form['refresh_token'].value,
        	            'client_id' : 'BHJJXLewp3VFBhgOY1T7NVlyXGsOtMF1',
        	            'client_secret' : 'PnpXEjNU4xKiwp69q6pBTrva04Ez94arfCXvg9n3FxVwG5DQN7tUBnSKN7NFc5ch' }

	r = requests.post(url, params = payload)

	payload = json.loads(r.text)
	print(payload)

	if 'error' in payload:
		print("Error: " + payload['error'])
	else:
		print(payload['user_id'])
		cur.execute("select * from users where id=%s", (payload['user_id'],))
		results = cur.fetchall()
		if len(results) > 0:
			cur.execute("update users set access_token=%s, refresh_token=%s, token_type=%s, expires_in=%s, last_update=%s where id=%s", (payload['access_token'], payload['refresh_token'], payload['token_type'], payload['expires_in'],time.time(),payload['user_id'],))
			con.commit()
		else:
			cur.execute("insert into users (id, access_token, refresh_token, token_type, expires_in, last_update) values (%s, %s, %s, %s, %s, %s)", (payload['user_id'], payload['access_token'], payload['refresh_token'], payload['token_type'], payload['expires_in'],time.time(),))
			con.commit()

