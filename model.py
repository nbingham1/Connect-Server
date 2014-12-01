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
	model_interval = 4

	users = get_users(con, cur, user_id)
	week = get_places(con, cur, user_id, 7)
	weeks = get_places(con, cur, user_id, 7*10)
	friends = get_friends(con, cur, user_id)
	get_radius_history(users, week, friends)
	get_radius_mean(friends)
	get_radius_std(friends)
	get_current_radius(users, friends)
	get_week_mean(users, weeks, model_interval)
	get_week_std(users, weeks, model_interval)

	suggestions = []
	for friend in friends:
		if friend['current_radius'] <= friend['radius_mean'] - friend['radius_std']:
			if long(friend['user1_id']) == long(user_id):
				for user in users:
					if user['id'] == friend['user2_id']:
						suggestions.append({'name':user['name'], 'time':'now', 'reason':'Your friend is nearby.'})
			elif long(friend['user2_id']) == long(user_id):
				for user in users:
					if user['id'] == friend['user1_id']:
						suggestions.append({'name':user['name'], 'time':'now', 'reason':'Your friend is nearby.'})
	
		weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
		for user1 in users:
			if user1['id'] == friend['user1_id']:
				for user2 in users:
					if user2['id'] == friend['user2_id']:
						for h in range(0, 24*7/model_interval):
							if user1['week'][h]['lat'] is not None and user1['week'][h]['lon'] is not None and user2['week'][h]['lat'] is not None and user2['week'][h]['lon'] is not None:
								distance = get_distance(user1['week'][h]['lat'], user1['week'][h]['lon'], user2['week'][h]['lat'], user2['week'][h]['lon'])
								if distance < max(user1['week'][h]['radius'], 200) and distance < max(user2['week'][h]['radius'], 200):
									t = weekday_names[h*model_interval/24] + ' between ' + datetime.strptime(str((h*model_interval)%24), "%H").strftime("%I %p") + ' and ' + datetime.strptime(str(((h+1)*model_interval)%24), "%H").strftime("%I %p")
									if long(user1['id']) == long(user_id):
										suggestions.append({'name':user2['name'], 'time':t, 'reason':'Your friend generally hangs out near where you do around this time.'})
									elif long(user2['id']) == long(user_id):
										suggestions.append({'name':user1['name'], 'time':t, 'reason':'Your friend generally hangs out near where you do around this time.'})
	
	return suggestions

