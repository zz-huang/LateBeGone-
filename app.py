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

	stopsList = []

	# load and get Route & Direction
	parseRoute = request.get_json()

	# get Route from prev JSON, create stopsByRoute url, load 
	stopsURL = "https://api-v3.mbta.com/stops?filter%5Broute%5D="+str(getRoute(parseRoute))
	# parseStops=requests.get(stopsURL)
	stopsjson = urllib.urlopen(stopsURL)
	# array=json.dumps(jsonurl)
	parseStops = json.loads(stopsjson.read())

	getStops(parseStops)
	direction = getDirection(parseRoute)
	returnStops = getOrder(direction)

	exportStops = json.dumps(returnStops)

	return exportStops

# when request for stop prediction is sent
@app.route('/prediction', methods=['POST'])
def sendPredictions():

	jsonStop = request.get_json()

	'''
	More backend code
	'''

	return # JSON file

# get route name from JSON
def getRoute(parseRoute):
    routeName = parseRoute.route
    # routeName = "Red"
    return routeName

# create list of stop names
def getStops(parseStops, stopsList):
	for i in range(len(parseStops["data"])):
		data = parseStops["data"][i]["attributes"]["name"]
		stopsList.append(data)

# get direction name from JSON
def getDirection(parseRoute):
    directionName = parseRoute.direction
    # directionName = "Inbound"
    return directionName

def getOrder(direction):
	zero = ["Outbound","Southbound","Westbound","South Station"]
	one = ["Inbound","Northbound","Eastbound","TF Green Airport"]
	if direction in zero:
		return stopsList
	if direction in one:
		return stopsList[::-1]

if __name__ == '__main__':
    app.run(debug=True)