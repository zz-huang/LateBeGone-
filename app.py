import json
import requests
import os
import math
import apikeys

from flask import *
from pymongo import MongoClient
from jsonschema import validate, ValidationError

app = Flask(__name__)
client = MongoClient()
db = client['database411']

# displays web form
@app.route('/', methods=['GET'])
def main_page():
	return render_template('main.html')

# displays login page
@app.route('/login', methods=['GET','POST'])
def login_page():
	
	# ### following block validates account creations; will probably need to move/adjust
	# if request.method == 'POST':
	# 	with open('schema.json') as schema:
	# 		schema = json.load(schema)
	# 	try:
	# 		new_user = request.get_json()
	# 		validate(new_user, schema)
	# 		'''
	# 		local_pass_hash = hash(new_user["local"]["password"])
	# 		new_user["local"]["password"] = local_pass_hash
	# 		'''
	# 		result = db.users.insert_one(new_user)
	# 	except ValidationError:
	# 		print('Schema Error: Incoming JSON could not be validated.')

	# ### folowing block validates account logins; will probably need to move/adjust
	# if request.method == 'POST':
	# 	with open('schema.json') as schema:
	# 		schema = json.load(schema)
	# 	try:
	# 		user = request.get_json()
	# 		validate(user, schema)
	# 		username = user["local"]["username"]
	# 		result = db.users.find({"username": username})
	# 		'''
	# 		if no result:
	# 			user does not exist in db, send alert
			
	# 		if hash(user["local"]["password"] = result["local"]["password"]):
	# 			allow user to login
	# 		else:
	# 			send incorrect password alert
	# 		'''
	# 	except ValidationError:
	# 		print('Schema Error: Incoming JSON could not be validated.')

	return render_template('login.html')

# displays route page
@app.route('/route', methods=['GET'])
def route_page():
	return render_template('route.html')


#http://realtime.mbta.com/developer/api/v2/stopsbyroute?api_key=<key>&route=Orange&format=json
# when request for stop list is sent
@app.route('/stops', methods=['POST'])
def sendStops():
	jsonFront = request.get_json()
#	print (jsonFront)
	route = jsonFront["route"]
	direction = jsonFront["direction"]

	mbtakey = apikeys.mbta_key

	stopsURL = "https://api-v3.mbta.com/stops?api_key="+ (mbtakey)+"&filter%5Broute%5D=" + str(route)
	stopsDATA = requests.get(stopsURL)
	stopsJSON = stopsDATA.json()

	returnStops = getStops(stopsJSON, direction)

	exportStops = json.dumps(returnStops)
	return jsonify(exportStops)

# when request for stop prediction is sent
@app.route('/prediction', methods=['POST'])
def sendPredictions():
    jsonFront = request.get_json()
    stop = jsonFront["stop"]
    route = jsonFront["route"]
    direction = jsonFront["direction"]
    direction_id = getDirectionID(direction)

    mbtakey = apikeys.mbta_key

    predictionURL = "https://api-v3.mbta.com/predictions?api_key="+ (mbtakey)+"&filter[stop]=" + str(stop)
    predictionDATA = requests.get(predictionURL)
    predictionJSON = predictionDATA.json()
    returnPredictions = getPredictions(predictionJSON, route, direction_id)

    exportPrediction = json.dumps(returnPredictions)

    return jsonify(exportPrediction)

@app.route('/uber', methods=['POST'])

def sendUber():
    jsonFront = request.form.to_dict()
    startlat = jsonFront["startlat"]
    startlong = jsonFront["startlong"]
    endlat = jsonFront["endlat"]
    endlong = jsonFront["endlong"]

    url = 'https://sandbox-api.uber.com/v1/estimates/price'

    parameters = {
      'server_token': apikeys.uber_key,
      'start_latitude': float(startlat),
      'start_longitude': float(startlong),
      'end_latitude': float(endlat),
      'end_longitude': float(endlong),
    }

    response = requests.get(url, params=parameters)
    data = getUberPrices(response.json())

    return jsonify(data)

@app.route('/lyft', methods=['POST'])

def sendLyft():
    jsonFront = request.form.to_dict()
    startlat = jsonFront["startlat"]
    startlong = jsonFront["startlong"]
    endlat = jsonFront["endlat"]
    endlong = jsonFront["endlong"]

    url = 'https://api.lyft.com/v1/cost'

    parameters = {
      'Authorization': apikeys.lyft_key,
      'start_lat': float(startlat),
      'start_lng': float(startlong),
      'end_lat': float(endlat),
      'end_lng': float(endlong),
    }

    response = requests.get(url, params=parameters)
    data = getLyftPrices(response.json())
    return jsonify(data)

def getStops(stopsJSON, direction):
	stopsList = []
	for i in range(len(stopsJSON["data"])):
	    stopsDict = {}
	    name = stopsJSON["data"][i]["attributes"]["name"]
	    stop_id = stopsJSON["data"][i]["id"]
	    stopsDict["name"] = name
	    stopsDict["id"] = stop_id
	    stopsList.append(stopsDict)
	getOrder(stopsList, direction)
	return stopsList

def getPredictions(predictionJSON, route, direction_id):
    dataList = []
    for i in range(len(predictionJSON["data"])):
        dataDict = {}
        dataDict["Next Arrival"] = predictionJSON["data"][i]["attributes"]["arrival_time"][11:19]
        dataList.append(dataDict)
    return dataList

def getOrder(stopsList, direction):
	zero = ["Outbound","Southbound","Westbound","South Station"]
	one = ["Inbound","Northbound","Eastbound","TF Green Airport"]
	if direction in zero:
		return stopsList
	if direction in one:
		return stopsList[::-1]

def getDirectionID(direction):
	zero = ["Outbound","Southbound","Westbound","South Station"]
	one = ["Inbound","Northbound","Eastbound","TF Green Airport"]
	if direction in zero:
		return 0
	if direction in one:
		return 1

def getUberPrices (uberJSON):
    uberList = []
    # carDict={}
    cars = ["POOL", "uberX", "uberXL"]
    for i in range(len(uberJSON['prices'])-1):
        if uberJSON['prices'][i]['display_name'] in cars:
            entry={}
            name = uberJSON["prices"][i]["display_name"]
            highestimate = uberJSON["prices"][i]["high_estimate"]
            lowestimate = uberJSON["prices"][i]["low_estimate"]
            surge = uberJSON["prices"][i]["surge_multiplier"]
            price = uberSurge(surge, lowestimate, highestimate)
            entry["name"]=name
            entry["price"]=price
            uberList.append(entry)
    return uberList

def uberSurge (surge, lowestimate, highestimate):
    low = float(lowestimate) * float(surge)
    high = float(highestimate) * float(surge)
    return "$" + str(round(low,2))+ "-"+str(round(high,2))

def getLyftPrices (lyftJSON):
    lyftList = []
    cars = ["lyft_line", "lyft", "lyft_plus"]
    for i in range(len(lyftJSON["cost_estimates"])):
        if lyftJSON['cost_estimates'][i]['ride_type'] in cars:
            entry={}
            name = lyftJSON["cost_estimates"][i]["ride_type"]
            highestimate = lyftJSON["cost_estimates"][i]["estimated_cost_cents_max"]
            lowestimate = lyftJSON["cost_estimates"][i]["estimated_cost_cents_min"]
            surge = lyftJSON["cost_estimates"][i]["primetime_percentage"][:-1]
            price = lyftSurge(surge, lowestimate, highestimate)
            entry["name"]=name
            entry["price"]=price
            lyftList.append(entry)
    return lyftList

def lyftSurge (surge, lowestimate, highestimate):
    surge = "0."+str(surge)
    low = float(lowestimate/100.00) * float(surge) + float(lowestimate/100.00)
    high = float(highestimate/100.00) * float(surge) + float(highestimate/100.00)
    return "$" + str(round(low,2))+ "-"+str(round(high,2))

if __name__ == '__main__':
    app.run(debug=True)
