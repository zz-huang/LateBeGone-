import json
import requests
import urllib
from flask import *

app = Flask(__name__)
exportStops = ""
exportPrediction = ""

# displays web form
@app.route('/', methods=['GET'])
def index():
	return render_template('route.html')

# when request for stop list is sent
@app.route('/stops', methods=['POST'])
def sendStops():
		jsonFront = request.get_json()
		printthis=json.dumps(jsonFront)
		print(printthis)
		route = jsonFront["route"]
		direction = jsonFront["direction"]

		stopsURL = "https://api-v3.mbta.com/stops?filter%5Broute%5D="+str(route)
		stopsDATA = urllib.urlopen(stopsURL)
		stopsJSON = json.loads(stopsDATA.read())

		returnStops = getStops(stopsJSON, direction)
		
		global exportStops
		exportStops = json.dumps(returnStops)
		print(exportStops)
		return jsonify(exportStops)
# when request for stop prediction is sent

@app.route('/prediction', methods=['POST','GET'])
def sendPredictions():

	if request.method == 'POST':
		# load and get Stop, Route, & Direction
		jsonFront = request.get_json()

		json.dumps(jsonFront)
		# print (jsonFront)
		stop = jsonFront["stop"]
		route = jsonFront["route"]
		direction = jsonFront["direction"]
		direction_id = getDirectionID(direction)

		# load and get all predictions for stop
		predictionURL = "https://api-v3.mbta.com/predictions?filter[stop]={}".format(stop)
		predictionDATA = urllib.urlopen(predictionURL)
		predictionJSON = json.loads(predictionDATA.read())

		predictionURL = "https://api-v3.mbta.com/predictions?filter[stop]={}".format(stop)
		print (predictionURL)
		predictionDATA = urllib.urlopen(predictionURL)
		predictionJSON = json.loads(predictionDATA.read())
		for i in range(len(predictionJSON["data"])):
			if (predictionJSON["data"][i]["relationships"]["route"] == route and
				predictionJSON["data"][i]["attributes"]["direction_id"] == direction_id):
				depart_time = predictionJSON["data"][i]["attributes"]["departure_time"]
				arrive_time = predictionJSON["data"][i]["attributes"]["arrival_time"]

		data = {
			"departure_time": depart_time,
			"arrival_time": arrive_time
		}
		global exportPrediction
		exportPrediction = json.dumps(data)
		return Response(exportPrediction, mimetype='application/json')

	print("ELSE")
	print(exportPrediction)
	return Response(json.dumps(exportPrediction), mimetype='application/json')

def getStops(stopsJSON, direction):
	stopsList = []
	# stopsidList= []
	stopsDict = {}
	for i in range(len(stopsJSON["data"])):
	    stopsDict = {}
	    name = stopsJSON["data"][i]["attributes"]["name"]
	    stop_id = stopsJSON["data"][i]["id"]
	    stopsDict["name"]=name
	    stopsDict["id"]=stop_id
	    stopsList.append(stopsDict)
	    getOrder(stopsList, direction)
#	stopsDict["data"]=str(stopsList)
	return stopsList

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