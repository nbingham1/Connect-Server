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

print("Content-type: text/plain\r\n")
if 'code' in form or 'refresh_token' in form:
	url='https://api.moves-app.com/oauth/v1/access_token'
	payload={}
	if 'code' in form:
		payload = { 'grant_type' : 'authorization_code',
			    'code' : form['code'].value,
			    'client_id' : 'BHJJXLewp3VFBhgOY1T7NVlyXGsOtMF1',
			    'client_secret' : 'PnpXEjNU4xKiwp69q6pBTrva04Ez94arfCXvg9n3FxVwG5DQN7tUBnSKN7NFc5ch', 
			    'redirect_uri' : 'http://connect.sol-union.com/auth.py' }
	elif 'refresh_token' in form:
	        payload = { 'grant_type' : 'refresh_token',
        	            'refresh_token' : form['refresh_token'].value,
        	            'client_id' : 'BHJJXLewp3VFBhgOY1T7NVlyXGsOtMF1',
        	            'client_secret' : 'PnpXEjNU4xKiwp69q6pBTrva04Ez94arfCXvg9n3FxVwG5DQN7tUBnSKN7NFc5ch' }

	r = requests.post(url, params = payload)

	print(r.text)

	payload = json.loads(r.text)
	if 'error' in payload:
		print("Error: " + payload['error'])
	else:
		cur.execute("select * from users where id=%s", (payload['user_id'],))
		results = cur.fetchall()
		if len(results) > 0:
			cur.execute("update users set access_token=%s, refresh_token=%s, token_type=%s, expires_in=%s, last_update=%s where id=%s", (payload['access_token'], payload['refresh_token'], payload['token_type'], payload['expires_in'],time.time(),payload['user_id'],))
			con.commit()
		else:
			cur.execute("insert into users (id, access_token, refresh_token, token_type, expires_in, last_update) values (%s, %s, %s, %s, %s, %s)", (payload['user_id'], payload['access_token'], payload['refresh_token'], payload['token_type'], payload['expires_in'],time.time(),))
			con.commit()

