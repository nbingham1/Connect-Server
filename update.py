#!/usr/bin/python
import cgi, cgitb
import requests
import MySQLdb as db
import time
import datetime
from datetime import datetime
import json
import sys
from model import model

sys.stderr = sys.stdout

con = db.connect('localhost', 'connect', 'socialize', 'connect')
cur = con.cursor()

form = cgi.FieldStorage()

def totimestamp(dt, epoch=datetime(1970,1,1)):
    td = dt - epoch
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 1e6 

def check_location_and_add(lat, lon):
	cur.execute("select id from locations where lat=%s and lon=%s", (lat,lon,))
        results = cur.fetchall()
	if len(results) == 0:
		cur.execute("insert into locations (lat,lon) values (%s, %s)", (lat, lon,))
		con.commit()
		return cur.lastrowid
	else:
		return results[0][0]

def check_place_and_add(user_id, location_id, start, end, place_name):
	cur.execute("select user_id,location_id,start,end,place from places where location_id=%s and start=%s and end=%s", (location_id,start,end,))
	results = cur.fetchall()
	if len(results) == 0:
		cur.execute("insert into places (user_id, location_id, start, end, place) values (%s, %s, %s, %s, %s)", (user_id, location_id, start, end, place_name,))
		con.commit()
	return

def check_transport_and_add(user_id, start_location, end_location, start_time, end_time, activity):
	cur.execute("select user_id,start_location,end_location,start_time,end_time,activity from transport where user_id=%s and start_location=%s and end_location=%s and start_time=%s and end_time=%s", (user_id, start_location, end_location, start_time, end_time,))
	results = cur.fetchall()
	if len(results) == 0:
		cur.execute("insert into transport (user_id,start_location,end_location,start_time,end_time,activity) values(%s, %s, %s, %s, %s, %s)", (user_id, start_location, end_location, start_time, end_time, activity,))
		con.commit()
	return

print("Content-type: text/plain\r\n")
if 'user' in form:
	user_id = form['user'].value

	cur.execute("select access_token,last_update from users where id=%s", (user_id,))
        results = cur.fetchall()
	
	if len(results) > 0:
		access_token = results[0][0]
		old_timestamp = results[0][1]
		timestamp = time.time()
	
		old_timestamp = float(old_timestamp) - 60*60*24*5	

		url = 'https://api.moves-app.com/api/1.1/user/storyline/daily'
		payload = {'access_token' : access_token, 'pastDays' : int((60*60*24 - 1 + timestamp - float(old_timestamp))/(60*60*24)), 'updatedSince' : datetime.fromtimestamp(old_timestamp).strftime("%Y%m%dT%H%M%SZ"), 'trackPoints' : 'true'}

		r = requests.get(url, params = payload)

	    	payload = json.loads(r.text)

		for day in payload:
			if 'segments' in day:
				for segment in day['segments']:
					if 'type' in segment and segment['type'] == 'place':
						start_time = None
						end_time = None
	
						if 'startTime' in segment:
							start_time = totimestamp(datetime.strptime(segment['startTime'][:-5], "%Y%m%dT%H%M%S"))
						if 'endTime' in segment:
							end_time = totimestamp(datetime.strptime(segment['endTime'][:-5], "%Y%m%dT%H%M%S"))
	
						if 'place' in segment:
							place_name = None

							place = segment['place']
							if 'name' in place:
								place_name = place['name']

							if 'location' in place:
								lat = None
								lon = None
								start_location = None
	
								location = place['location']							
								if 'lat' in location:
									lat = location['lat']
								if 'lon' in location:
									lon = location['lon']
							
								if lat is not None and lon is not None:
									start_location = check_location_and_add(lat, lon)
							
							if start_location is not None and start_time is not None and end_time is not None:
								check_place_and_add(user_id, start_location, start_time, end_time, place_name)
					elif 'type' in segment and segment['type'] == 'move':
						if 'activities' in segment:
							activities = segment['activities']
							for activity in activities:
								start_location = None
								end_location = None
								start_time = None
								end_time = None
								activity_name = None
		
								if 'activity' in activity:
									activity_name = activity['activity']
									
								if 'trackPoints' in activity:
									trackPoints = activity['trackPoints']
									for trackPoint in trackPoints:
										lat = None
										lon = None
										start_time = end_time
										end_time = None
										start_location = end_location
										end_location = None
	
										if 'lat' in trackPoint:
											lat = trackPoint['lat']
										if 'lon' in trackPoint:
											lon = trackPoint['lon']
										if 'time' in trackPoint:
											end_time = totimestamp(datetime.strptime(trackPoint['time'][:-5], "%Y%m%dT%H%M%S"))
	
										if lat is not None and lon is not None:
											end_location = check_location_and_add(lat, lon)
										
										if start_time is not None and end_time is not None and start_location is not None and end_location is not None:
											check_transport_and_add(user_id, start_location, end_location, start_time, end_time, activity_name)
							
					else:
						print("error: unhandled segment\n" + str(segment))
	model(con, cur, user_id)
