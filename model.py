#!/usr/bin/python
import cgi, cgitb
import requests
import MySQLdb as db
import time
import datetime
from datetime import datetime
import json
import sys
import math
from modelapi import *

def model(con, cur, user_id):
	users = get_users(con, cur, user_id)
	places = get_places(con, cur, user_id)
	friends = get_friends(con, cur, user_id)
	normal_radii(users, places, friends)
	current_radii(users, friends)
	
	suggestions = []
	for friend in friends:
		if friend['current_radius'] < friend['normal_radius']:
			if long(friend['user1_id']) == long(user_id):
				for user in users:
					if user['id'] == friend['user2_id']:
						suggestions.append(user['name'])
			elif long(friend['user2_id']) == long(user_id):
				for user in users:
					if user['id'] == friend['user1_id']:
						suggestions.append(user['name'])
	

	return suggestions

