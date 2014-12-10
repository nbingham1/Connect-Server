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

# returns an array of users:
# {id, lat, lon, name}
def get_users(con, cur, user_id):
	cur.execute("select u.id,u.lat,u.lon,u.name from users as u join friends as f on (u.id=f.user1_id or u.id=f.user2_id) where (f.user1_id=%s or f.user2_id=%s)", (user_id, user_id,))
	results = cur.fetchall()
	users = []
	for result in results:
		users.append({'id':result[0], 'lat':result[1], 'lon':result[2], 'name':result[3]})
	return users

# returns an array of places:
# {user_id, start_time, end_time, name, lat, lon}
def get_places(con, cur, user_id, days):
	cur.execute("select * from places as p join friends as f inner join locations as l on p.location_id=l.id and (p.user_id=f.user1_id or p.user_id=f.user2_id) where end>%s and (f.user1_id=%s or f.user2_id=%s)", (int(time.time() - 60*60*24*days), user_id, user_id,))
	results = cur.fetchall()
	places = []
	for result in results:
		places.append({'user_id':result[0], 'start_time':result[2], 'end_time':result[3], 'name':result[4], 'lat':result[10], 'lon':result[11]})
	return places

# returns an array of friends:
# {user1_id, user2_id}
def get_friends(con, cur, user_id):
	cur.execute("select * from friends where user1_id = %s or user2_id = %s", (int(user_id), int(user_id),))
	results = cur.fetchall()
	friends = []
	for friend in results:
		friends.append({'user1_id':friend[0], 'user2_id': friend[1]})	
	return friends

#get_interest_score(friends, user_id)
def get_interest_score(con, cur, suggestions, user_id):
    cur.execute("select * from interests where user=%s", (int(user_id),))
    results = cur.fetchall()
    for friend in suggestions:
        print friend
        score = 0.0
        cur.execute("select * from interests where user=%s", (int(friend['id']),))
        friend_results = cur.fetchall()
        for my_result in results:
            for friend_result in friend_results:
                if my_result[1] == friend_result[1]:
                    score += float(my_result[2]) * float(friend_result[2])
        friend['score'] = score
    suggestions = sorted(suggestions, key=lambda k: k['score'], reverse=True) 
    if len(suggestions) == 0:
        return []
    else:
        return suggestions

# adds radius_history to each friend:
# {user1_id, user2_id, radius_history}
def get_radius_history(users, places, friends):
	for friend in friends:
		friend['radius_history'] = []
	
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
							friend['radius_history'].append(get_distance(places[users[min_user]['last_index']]['lat'], places[users[min_user]['last_index']]['lon'], places[user['last_index']]['lat'], places[user['last_index']]['lon']))

	for user in users:
		user.pop('done', None)
		user.pop('last_timestamp', None)
		user.pop('last_index', None)

	return

# adds radius_mean to each friend assuming they have radius_history:
# {user1_id, user2_id, radius_history, radius_mean}
def get_radius_mean(friends):
	for friend in friends:
		friend['radius_mean'] = 0
		count = 0
		for radius in friend['radius_history']:
			friend['radius_mean'] += radius 
			count += 1

		if count != 0:
			friend['radius_mean'] /= count
		else:
			friend['radius_mean'] = None
	return

# adds radius_std to each friend assuming they have radius_history and radius_mean:
# {user1_id, user2_id, radius_history, radius_mean, radius_std}
def get_radius_std(friends):
	for friend in friends:
		friend['radius_std'] = 0
		count = 0
		for radius in friend['radius_history']:
			if radius < friend['radius_mean']:
				friend['radius_std'] += (radius - friend['radius_mean'])*(radius - friend['radius_mean'])
				count += 1
		if count != 0:
			friend['radius_std'] /= count
			friend['radius_std'] = math.sqrt(friend['radius_std'])
		else:
			friend['radius_std'] = None
	return

# adds current radius to each friend:
# {user1_id, user2_id, current_radius}
def get_current_radius(users, friends):
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

# adds location_mean_history to each user:
# {id, lat, lon, name, location_mean_history}
def get_week_mean(users, places, interval):
	for user in users:
		user['week'] = []
		for i in range(0, 24*7/interval):
			user['week'].append({'lat':0,'lon':0,'radius':0,'count':0})
		
		for place in places:
			if place['user_id'] == user['id']:
				start = datetime.fromtimestamp(place['start_time'])
				end = datetime.fromtimestamp(place['end_time'])
				for h in range(start.hour, end.hour+1):
					hour_of_week = (start.weekday()*24+h)/interval
					user['week'][hour_of_week]['lat'] += place['lat']
					user['week'][hour_of_week]['lon'] += place['lon']
					user['week'][hour_of_week]['count'] += 1
		for h in user['week']:
			if h['count'] != 0:
				h['lat'] /= h['count']
				h['lon'] /= h['count']
			else:
				h['lat'] = None
				h['lon'] = None

	return

def get_week_std(users, places, interval):
	for user in users:
		for place in places:
			if place['user_id'] == user['id']:
				start = datetime.fromtimestamp(place['start_time'])
				end = datetime.fromtimestamp(place['end_time'])
				for h in range(start.hour, end.hour+1):
					hour_of_week = (start.weekday()*24+h)/interval
					radius = get_distance(place['lat'], place['lon'], user['week'][hour_of_week]['lat'], user['week'][hour_of_week]['lon'])
					user['week'][hour_of_week]['radius'] += radius*radius

		for h in user['week']:
			if h['count'] != 0:
				h['radius'] /= h['count']
				h['radius'] = math.sqrt(h['radius'])
			else:
				h['radius'] = None
	return
