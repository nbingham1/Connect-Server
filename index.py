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
if 'update' in form:
	user_id = form['update'].value

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
			print(day['date'])	
			for segment in day['segments']:
				start_time = None
				end_time = None
				place_name = None
				location_id = None
				start_lat = None
				start_lon = None
				end_lon = None
				end_lat = None
				activity = None
				
				if 'startTime' in segment:
					start_time = totimestamp(datetime.strptime(segment['startTime'][:-5], "%Y%m%dT%H%M%S"))
				if 'endTime' in segment:
					end_time = totimestamp(datetime.strptime(segment['endTime'][:-5], "%Y%m%dT%H%M%S"))
				
				if 'type' in segment and segment['type'] == 'place':
					if 'place' in segment:
						place = segment['place']
						if 'name' in place:
							place_name = place['name']
						if 'id' in place:
							location_id = place['id']

						if 'location' in place:
							location = place['location']							
							if 'lat' in location:
								start_lat = location['lat']
							if 'lon' in location:
								start_lon = location['lon']
							
							if 'id' in place:
								check_location_and_add(location_id, start_lat, start_lon)
		
						check_place_and_add(user_id, location_id, start_time, end_time, place_name)
				elif 'type' in segment and segment['type'] == 'move':
					if 'activities' in segment:
						activities = segment['activities']
						for activity in activities:
							start_lat = None
							end_lat = None
							start_lon = None
							end_lon = None
							start_time = None
							end_time = None

							if 'activity' in activity:
								print activity['activity']
								
							if 'trackPoints' in activity:
								trackPoints = activity['trackPoints']
								for trackPoint in trackPoints:
									if 'lat' in trackPoint:
										start_lat = end_lat
										end_lat = trackPoint['lat']
									if 'lon' in trackPoint:
										start_lon = end_lon
										end_lon = trackPoint['lon']
									if 'time' in trackPoint:
										start_time = end_time
										end_time = trackPoint['lon']

									if end_lat is not None and end_lon is not None:
										check_location_and_add(0, end_lat, end_lon)

									if start_time is not None and start_lon is not None and start_lat is not None:
										print(str(start_lat) + "->" + str(end_lat) + " " + str(start_lon) + "->" + str(end_lon) + " " + str(start_time) + "->" + str(end_time))
						
				else:
					print segment
#				if 'activities' in segment:
#					for activity in segment['activities']:
#						print activity
#						print	
#				elif 'place' in segment:
#					print segment
