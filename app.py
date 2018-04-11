import json
import requests
from flask import *

app = Flask(__name__)

# displays web form
@app.route('/', methods=['GET'])
def index():
	return render_template('route.html')

# when request for stop list is sent
@app.route('/stops', methods=['POST'])
def sendStops():
	jsonFront = request.get_json()
	route = jsonFront["route"]
	direction = jsonFront["direction"]

	stopsURL = "https://api-v3.mbta.com/stops?filter%5Broute%5D=" + str(route)
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

    predictionURL = "https://api-v3.mbta.com/predictions?filter[stop]=" + str(stop)
    predictionDATA = requests.get(predictionURL)
    predictionJSON = predictionDATA.json()

    returnPredictions = getPredictions(predictionJSON, route, direction_id)

    exportPrediction = json.dumps(returnPredictions)
    return jsonify(exportPrediction)

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
        if (predictionJSON["data"][i]["relationships"]["route"]["data"]["id"] == route and
            predictionJSON["data"][i]["attributes"]["direction_id"] == direction_id): #and counter<=3:
            dataDict = {}
            dataDict["Next Arrival"] = predictionJSON["data"][i]["attributes"]["arrival_time"][11:19]
            dataDict["Next Departure"] = predictionJSON["data"][i]["attributes"]["departure_time"][11:19]
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

if __name__ == '__main__':
    app.run(debug=True)