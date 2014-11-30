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

def normal_radii():
	return

def model(con, cur, user_id):
	cur.execute("select u.id,u.lat,u.lon from users as u join friends as f on (u.id=f.user1_id or u.id=f.user2_id) where (f.user1_id=%s or f.user2_id=%s)", (user_id, user_id,))
	results = cur.fetchall()
	users = []
	for result in results:
		users.append({'id':result[0], 'lat':result[1], 'lon':result[2], 'last_timestamp':0, 'last_index':0, 'done':False})

	print("\n\nPlaces")
	cur.execute("select * from places as p join friends as f inner join locations as l on p.location_id=l.id and (p.user_id=f.user1_id or p.user_id=f.user2_id) where end>%s and (f.user1_id=%s or f.user2_id=%s)", (int(time.time() - 60*60*24*7), user_id, user_id,))
	places = cur.fetchall()
	for place in places:
		print(place)

	print("\n\nFriends")
	cur.execute("select * from friends where user1_id = %s or user2_id = %s", (int(user_id), int(user_id),))
	results = cur.fetchall()
	friends = []
	for friend in results:
		friends.append({'user1_id':friend[0], 'user2_id': friend[1], 'normal_radius':0, 'data_count':0})	
	print(friends)

	print("\n\nUsers")
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
			if places[i][0] == users[min_user]['id'] and places[i][3] > users[min_user]['last_timestamp'] and places[i][3] < min_timestamp:
				min_timestamp = places[i][3]
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
							friend['normal_radius'] += get_distance(places[users[min_user]['last_index']][10], places[users[min_user]['last_index']][11], places[user['last_index']][10], places[user['last_index']][11])
							friend['data_count'] += 1

	print("\n\nResults")
	for friend in friends:
		friend['normal_radius'] /= friend['data_count']
		friend.pop('data_count', None)
		print(friend)

	return

sys.stderr = sys.stdout

con = db.connect('localhost', 'connect', 'socialize', 'connect')
cur = con.cursor()

form = cgi.FieldStorage()

print("Content-type: text/plain\r\n")
model(con, cur, form['user'].value)
