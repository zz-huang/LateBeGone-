import json
import requests
import urllib
from flask import *

app = Flask(__name__)

# displays web form
@app.route('/', methods=['GET'])
def index():
	return render_template("route.html")

# when request for stop list is sent
@app.route('/stops', methods=['POST'])
def sendStops():

	# load and get Route & Direction
	jsonFront = request.get_json()
	route = jsonFront["route"]
	direction = jsonFront["direction"]

	# load and get all stops for route
	stopsURL = "https://api-v3.mbta.com/stops?filter%5Broute%5D="+str(route)
	stopsDATA = urllib.urlopen(stopsURL)
	stopsJSON = json.loads(stopsDATA.read())

	# filter out stops for route in direction
	stopsList = getStops(stopsJSON)
	returnStops = getOrder(stopsList, direction)

	# create and export JSON of stops for route in direction
	exportStops = json.dumps(returnStops)
	return exportStops

# when request for stop prediction is sent
@app.route('/prediction', methods=['POST'])
def sendPredictions():

	# load and get Stop, Route, & Direction
	jsonFront = request.get_json()
	stop = jsonFront["stop"]
	route = jsonFront["route"]
	direction = jsonFront["direction"]
	direction_id = getDirectionID(direction)

	# load and get all predictions for stop
	predictionURL = "https://api-v3.mbta.com/predictions?filter[stop]={}".format(stop)
	predictionDATA = urllib.urlopen(predictionURL)
	predictionJSON = json.loads(predictionDATA.read())

	# parse JSON for desired prediction
	for i in range(len(predictionJSON["data"])):
		if (predictionJSON["data"][i]["relationships"]["route"] == route and
			predictionJSON["data"][i]["attributes"]["direction_id"] == direction_id):
			depart_time = predictionJSON["data"][i]["attributes"]["departure_time"]
			arrive_time = predictionJSON["data"][i]["attributes"]["arrival_time"]

	# assemble data
	data = {
		"departure_time": depart_time,
		"arrival_time": arrive_time
	}

	# create and export JSON of prediction for stop in route in direction
	exportPrediction = json.dumps(data)
	return exportPrediction

# create list of stop names
def getStops(stopsJSON):
	stopsList = []
	for i in range(len(stopsJSON["data"])):
		data = stopsJSON["data"][i]["attributes"]["name"]
		stopsList.append(data)
	return stopsList

# determine order of 'stopsList'
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