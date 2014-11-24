#!/usr/bin/python
import cgi, cgitb
import requests
import MySQLdb as db
import time
import datetime
import json
import sys

#testing connectivity

sys.stderr = sys.stdout

print("Content-type: text/plain\r\n\r\n")

con = db.connect('localhost', 'connect', 'socialize', 'connect')
cur = con.cursor()

form = cgi.FieldStorage()

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
elif 'update' in form:
	user_id = form['update'].value

	cur.execute("select access_token,last_update from users where id=%s", (user_id,))
        results = cur.fetchall()
	

	if len(results) > 0:
		access_token = results[0][0]
		old_timestamp = results[0][1]
		timestamp = time.time()
	
		old_timestamp = float(old_timestamp) - 60*60*24*5	

		url = 'https://api.moves-app.com/api/1.1/user/storyline/daily'
		payload = {'access_token' : access_token, 'pastDays' : int((60*60*24 - 1 + timestamp - float(old_timestamp))/(60*60*24)), 'updatedSince' : datetime.datetime.fromtimestamp(old_timestamp).strftime("%Y%m%dT%H%M%SZ"), 'trackPoints' : 'true'}

		r = requests.get(url, params = payload)

	        payload = json.loads(r.text)

		for day in payload:
			print(day['date'])	
			for segment in day['segments']:
				print segment
#				if 'activities' in segment:
#					for activity in segment['activities']:
#						print activity
#						print	
#				elif 'place' in segment:
#					print segment
