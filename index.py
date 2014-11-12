#!/usr/bin/python
import cgi, cgitb
import requests

form = cgi.FieldStorage()

# headers
print("Content-type: test/html\r\n\r\n")

if 'code' in form:
	url = 'https://api.moves-app.com/oauth/v1/access_token'
	payload = { 'grant_type' : 'authorization_code',
		    'code' : form['code'],
		    'client_id' : 'BHJJXLewp3VFBhgOY1T7NVlyXGsOtMF1',
		    'client_secret' : 'PnpXEjNU4xKiwp69q6pBTrva04Ez94arfCXvg9n3FxVwG5DQN7tUBnSKN7NFc5ch', 
		    'redirect_uri' : 'http://connect.sol-union.com/index.py' }
	r = requests.get(url, params = payload);
	print(r.text);
elif 'refresh_token' in form:
	url = 'https://api.moves-app.com/oauth/v1/access_token'
	payload = { 'grant_type' : 'refresh_token',
		    'refresh_token' : form['refresh_token'],
		    'client_id' : 'BHJJXLewp3VFBhgOY1T7NVlyXGsOtMF1',
		    'client_secret' : 'PnpXEjNU4xKiwp69q6pBTrva04Ez94arfCXvg9n3FxVwG5DQN7tUBnSKN7NFc5ch' }
	r = requests.get(url, params = payload);
	print(r.text);

