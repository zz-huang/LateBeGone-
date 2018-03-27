import urllib
import json
import requests
    
stopsList=[]
#get route name from JSON
def getRoute():
    routeName=parseRoute.route
#get direction name from JSON
def getDirection():
    directionName=parseRoute.direction

#get stop name from parsed JSON
def getName():
    stopName=stopsList.name

#create list of stop names
def getStops():
	while True:
		stopsList=parseStops["data"]["attributes"]["name"]

def getOrder(direction):
	zero=["Outbound","Southbound","Westbound","South Station"]
	one=["Inbound","Northbound","Eastbound","TF Green Airport"]
	if direction in zero:
		return stopsList
	if direction in one:
		return stopsList[::-1]
#load and get Route & Direction
routeURL= None  #insert front end JSON
parseRoute= requests.get(routeURL)


#get Route from prev JSON, create stopsByRoute url, load 
stopsURL= "https://api-v3.mbta.com/schedules?filter%5B"+str(getRoute())
parseStops=requests.get(stopsURL)

getStops()
direction=getDirection()
returnStops=getOrder(direction)

exportStops=json.dump(returnStops)




