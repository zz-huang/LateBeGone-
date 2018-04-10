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
		route = jsonFront["route"]
		direction = jsonFront["direction"]

		stopsURL = "https://api-v3.mbta.com/stops?filter%5Broute%5D="+str(route)
		stopsDATA = urllib.urlopen(stopsURL)
		stopsJSON = json.loads(stopsDATA.read())

		returnStops = getStops(stopsJSON, direction)
		
		global exportStops
		exportStops = json.dumps(returnStops)
		return jsonify(exportStops)
# when request for stop prediction is sent

@app.route('/prediction', methods=['POST'])
def sendPredictions():
    jsonFront = request.get_json()
    printthis=json.dumps(jsonFront)
    stop = jsonFront["stop"]
    route = jsonFront["route"]
    direction = jsonFront["direction"]
    direction_id = getDirectionID(direction)

    predictionURL = "https://api-v3.mbta.com/predictions?filter[stop]={}".format(stop)
    predictionDATA = urllib.urlopen(predictionURL)
    predictionJSON = json.loads(predictionDATA.read())
    counter = 0
    dataList = []
    for i in range(len(predictionJSON["data"])):
        if (predictionJSON["data"][i]["relationships"]["route"]["data"]["id"] == route and
            predictionJSON["data"][i]["attributes"]["direction_id"] == direction_id) and counter<=3:
            counter +=1
            dataDict = {}
            dataDict["Departure"] = predictionJSON["data"][i]["attributes"]["departure_time"]
            dataDict["arrive_time"] = predictionJSON["data"][i]["attributes"]["arrival_time"]
            dataList.append(dataDict)
    global exportPrediction
    exportPrediction = json.dumps(dataList)
    return jsonify(exportPrediction)

def getStops(stopsJSON, direction):
	stopsList = []
	for i in range(len(stopsJSON["data"])):
	    stopsDict = {}
	    name = stopsJSON["data"][i]["attributes"]["name"]
	    stop_id = stopsJSON["data"][i]["id"]
	    stopsDict["name"]=name
	    stopsDict["id"]=stop_id
	    stopsList.append(stopsDict)
	    getOrder(stopsList, direction)
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