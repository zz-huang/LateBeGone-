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
		stopsList=[]
		#get route name from JSON
		def getRoute():
		    routeName=parseRoute.route
		    # routeName = "Red"
		    return routeName
		#get direction name from JSON
		def getDirection():
		    directionName=parseRoute.direction
		    # directionName="Inbound"
		    return directionName

		#create list of stop names
		def getStops():
			for i in range(len(parseStops["data"])):
				data=parseStops["data"][i]["attributes"]["name"]
				stopsList.append(data)

		def getOrder(direction):
			zero=["Outbound","Southbound","Westbound","South Station"]
			one=["Inbound","Northbound","Eastbound","TF Green Airport"]
			if direction in zero:
				return stopsList
			if direction in one:
				return stopsList[::-1]

		#load and get Route & Direction
		# routeURL= None  #insert front end JSON
		# routejson = urllib.urlopen(stopsURL)
		# parseRoute= json.loads(routejson.read())


		#get Route from prev JSON, create stopsByRoute url, load 
		stopsURL= "https://api-v3.mbta.com/stops?filter%5Broute%5D="+str(getRoute())
		# parseStops=requests.get(stopsURL)
		stopsjson = urllib.urlopen(stopsURL)
		# array=json.dumps(jsonurl)
		parseStops = json.loads(stopsjson.read())

		getStops()
		direction=getDirection()
		returnStops=getOrder(direction)

		exportStops=json.dumps(returnStops)
		print exportStops

	return # JSON file

# when request for stop prediction is sent
@app.route('/prediction', methods=['POST'])
def sendPredictions():

	jsonStop = request.get_json()

	'''
	More backend code
	'''

	return # JSON file

if __name__ == '__main__':
    app.run(debug=True)
