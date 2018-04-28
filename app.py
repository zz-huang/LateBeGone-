from __future__ import unicode_literals

import json
import requests
import os
import math
import apikeys
import hashlib

from datetime import datetime
from time import sleep
from flask import *
from pymongo import MongoClient
from jsonschema import validate, ValidationError
from twilio.rest import Client
from flask_oauthlib.client import OAuth

app = Flask(__name__)
mongoClient = MongoClient()
db = mongoClient['database411']

app.secret_key = 'development'

oauth = OAuth(app)

twitter = oauth.remote_app(
    'twitter',
    consumer_key='xBeXxg9lyElUgwZT6AZ0A',
    consumer_secret='aawnSpNTOVuDCjx7HMh6uSXetjNN8zWLpZwCEU4LBrk',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize'
)


@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


#@app.route('/')
#def index():
#    tweets = None
#    if g.user is not None:
#        resp = twitter.request('statuses/home_timeline.json')
#        if resp.status == 200:
#            tweets = resp.data
#        else:
#            flash('Unable to load tweets from Twitter.')
#    return render_template('main.html', tweets=tweets)


@app.route('/tweet', methods=['POST'])
def tweet():
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    status = request.form['tweet']
    if not status:
        return redirect(url_for('index'))
    resp = twitter.post('statuses/update.json', data={
        'status': status
    })

    if resp.status == 403:
        flash("Error: #%d, %s " % (
            resp.data.get('errors')[0].get('code'),
            resp.data.get('errors')[0].get('message'))
        )
    elif resp.status == 401:
        flash('Authorization error with Twitter.')
    else:
        flash('Successfully tweeted your tweet (ID: #%s)' % resp.data['id'])
    return redirect(url_for('index'))


@app.route('/login')
def login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('index'))

@app.route('/', methods=['GET'])
def main_page():
	if not session.get('logged_in'):
		return redirect('/login_local')
	return render_template('main.html')

# displays login page
@app.route('/login_local', methods=['GET','POST'])
def login_local():
	if request.method == 'POST':
		user = request.get_json()
		username = user["local"]["username"]
		result = db.users.find({"username": username})

		if result.count() == 0:
			flash("Username not found")
			print("User does not exist in db")
		elif hash(user["local"]["password"]) == result["local"]["password"]:
			session['logged_in'] = True
			print("Login was successful")
			return redirect('/')
		else:
			flash("Password was incorrect")
			print("Password was incorrect")

	return render_template('login.html')

@app.route('/logout_local')
def logout_local():
	session['logged_in'] = False
	return redirect('/')

@app.route('/create', methods=['GET','POST'])
def create_page():
    if request.method == 'POST':
        new_user = request.get_json()

        check = db.users.find({"username": username})
        if check.count() != 0:
            print("Username already exists")
            return redirect('/create')

        with open('create_schema.json') as schema:
            schema = json.load(schema)
        try:
            validate(new_user, schema)
            local_pass_hash = hash(new_user["local"]["password"])
            new_user["local"]["password"] = local_pass_hash
            result = db.users.insert_one(new_user)
        except ValidationError:
            print('Schema Error: Incoming JSON could not be validated.')

    return render_template('create.html')

# displays route page
@app.route('/route', methods=['GET'])
def route_page():
	return render_template('route.html')

# http://realtime.mbta.com/developer/api/v2/stopsbyroute?api_key=<key>&route=Orange&format=json
# when request for stop list is sent
@app.route('/stops', methods=['POST'])
def sendStops():
	jsonFront = request.get_json()
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
        try:
            dataDict["Next Arrival"] = predictionJSON["data"][i]["attributes"]["arrival_time"][11:19]
        except:
            dataDict["Next Arrival"] = "No prediction found."
        dataList.append(dataDict)
        if (i == 0):
            firstPrediction = predictionJSON["data"][i]["attributes"]["departure_time"][11:19]
            sendText(firstPrediction)
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

def sendText(arrival_time):
    account_sid = apikeys.twilio_sid
    auth_token = apikeys.twilio_auth

    twilioClient = Client(account_sid, auth_token)

    ct=time.ctime()
    ct=ct[11:19]

    FMT = '%H:%M:%S'
    tdelta = datetime.strptime(arrival_time, FMT) - datetime.strptime(ct, FMT)
    tdelta= str(tdelta)
    diff= (sum(int(tdelta) * 60 ** i for i,tdelta in enumerate(reversed(tdelta.split(":")))))

    if diff < 300:
        twilioClient.api.account.messages.create(
            to= apikeys.mynum,
            from_= apikeys.twilionum,
            body="The MBTA is coming in " + tdelta + "minutes at " + str(arrival_time) + "! Get going!"
        )
    else:
        download_thread = threading.Thread(target=delayText, args= (arrival_time,diff))
        download_thread.start()

def delayText(arrival_time,x):

    account_sid = apikeys.twilio_sid
    auth_token = apikeys.twilio_auth

    twilioClient = Client(account_sid, auth_token)

    sleep(x-300)
    twilioClient.api.account.messages.create(
                to= apikeys.mynum,
                from_= apikeys.twilionum,
                body="The MBTA is coming in 5 minutes at " + str(arrival_time) + "!"
                
def emptyCache():
	result = db.cache.find()
	if result.count() == 0:
		print("Cache already empty")
	else:
		result = db.restaurants.delete_many({})
		print("Cache emptied of {} documents".format(result.deleted_count))

def hash(text):
    return hashlib.sha256(text.encode()).hexdigest() 

if __name__ == '__main__':
    app.run(debug=True)
