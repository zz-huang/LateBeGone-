import json
import requests
import os
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

# when request for stop list is sent
@app.route('/stops', methods=['POST'])
def sendStops():
	jsonFront = request.get_json()
	print (jsonFront)
	route = jsonFront["route"]
	direction = jsonFront["direction"]

	parameters = {
              'Key':'d12a26b5b2034ac0a364e7a8b36afbc1',
        }

	stopsURL = "https://api-v3.mbta.com/stops?filter%5Broute%5D=" + str(route)
	stopsDATA = requests.get(stopsURL,params=parameters)
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

    parameters = {
          'Key':'d12a26b5b2034ac0a364e7a8b36afbc1',
    }

    predictionURL = "https://api-v3.mbta.com/predictions?filter[stop]=" + str(stop)
    predictionDATA = requests.get(predictionURL, params=parameters)
    predictionJSON = predictionDATA.json()
    print (predictionJSON)
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
      'server_token':'API_KEY',
      'start_latitude': float(startlat),
      'start_longitude': float(startlong),
      'end_latitude': float(endlat),
      'end_longitude': float(endlong),
    }

    response = requests.get(url, params=parameters)

    data = json.dumps( response.json(), indent=2 )

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
      'Authorization':'API_KEY',
      'start_lat': float(startlat),
      'start_lng': float(startlong),
      'end_lat': float(endlat),
      'end_lng': float(endlong),
    }

    response = requests.get(url, params=parameters)

    data = json.dumps( response.json(), indent=2 )
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
        if (predictionJSON["data"][i]["relationships"]["route"]["data"]["id"] == route): #and
#            predictionJSON["data"][i]["attributes"]["direction_id"] == direction_id):
            dataDict = {}
            dataDict["Next Arrival"] = predictionJSON["data"][i]["attributes"]["arrival_time"][11:19]
#            dataDict["Next Departure"] = predictionJSON["data"][i]["attributes"]["departure_time"][11:19]
            dataList.append(dataDict)
#        id = getDirectionID(direction_id)
#        dataList.append({"direction_id": id})
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

if __name__ == '__main__':
    app.run(debug=True)
