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

def get_users(con, cur, user_id):
	cur.execute("select u.id,u.lat,u.lon,u.name from users as u join friends as f on (u.id=f.user1_id or u.id=f.user2_id) where (f.user1_id=%s or f.user2_id=%s)", (user_id, user_id,))
	results = cur.fetchall()
	users = []
	for result in results:
		users.append({'id':result[0], 'lat':result[1], 'lon':result[2], 'name':result[3]})
	return users

def get_places(con, cur, user_id):
	cur.execute("select * from places as p join friends as f inner join locations as l on p.location_id=l.id and (p.user_id=f.user1_id or p.user_id=f.user2_id) where end>%s and (f.user1_id=%s or f.user2_id=%s)", (int(time.time() - 60*60*24*7), user_id, user_id,))
	results = cur.fetchall()
	places = []
	for result in results:
		places.append({'user_id':result[0], 'start_time':result[2], 'end_time':result[3], 'name':result[4], 'lat':result[10], 'lon':result[11]})
	return places

def get_friends(con, cur, user_id):
	cur.execute("select * from friends where user1_id = %s or user2_id = %s", (int(user_id), int(user_id),))
	results = cur.fetchall()
	friends = []
	for friend in results:
		friends.append({'user1_id':friend[0], 'user2_id': friend[1]})	
	return friends

def normal_radii(users, places, friends):
	for friend in friends:
		friend['normal_radius'] = 0
		friend['data_count'] = 0
	
	for user in users:
		user['done'] = False
		user['last_timestamp'] = 0
		user['last_index'] = -1

	done = False
	while (not done):
		min_timestamp = time.time()
		min_user = -1
		
		for i in range(0, len(users)):
			if not users[i]['done'] and users[i]['last_timestamp'] < min_timestamp:
				min_timestamp = users[i]['last_timestamp']
				min_user = i
		
		min_timestamp = time.time()
		min_place = -1

		for i in range(0, len(places)):
			if places[i]['user_id'] == users[min_user]['id'] and places[i]['end_time'] > users[min_user]['last_timestamp'] and places[i]['end_time'] < min_timestamp:
				min_timestamp = places[i]['end_time']
				min_place = i				

		if min_place == -1:
			users[min_user]['done'] = True

			done = True
			for user in users:
				if not user['done']:
					done = False
		else:
			users[min_user]['last_timestamp'] = min_timestamp
			users[min_user]['last_index'] = min_place
			for friend in friends:
				if users[min_user]['id'] == friend['user1_id'] or users[min_user]['id'] == friend['user2_id']:
					for user in users:
						if user['id'] != users[min_user]['id'] and (user['id'] == friend['user1_id'] or user['id'] == friend['user2_id']):
							friend['normal_radius'] += get_distance(places[users[min_user]['last_index']]['lat'], places[users[min_user]['last_index']]['lon'], places[user['last_index']]['lat'], places[user['last_index']]['lon'])
							friend['data_count'] += 1

	for friend in friends:
		friend['normal_radius'] /= friend['data_count']
		friend.pop('data_count', None)

	for user in users:
		user.pop('done', None)
		user.pop('last_timestamp', None)
		user.pop('last_index', None)

	return

def current_radii(users, friends):
	for friend in friends:
		user1 = None
		user2 = None
		for user in users: 
			if user['id'] == friend['user1_id']:
				user1 = user
			if user['id'] == friend['user2_id']:
				user2 = user
		friend['current_radius'] = get_distance(user1['lat'], user1['lon'], user2['lat'], user2['lon'])
	return


