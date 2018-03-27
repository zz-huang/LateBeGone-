import json
import requests
from flask import *

app = Flask(__name__)

# displays web form
@app.route('/', methods=['GET'])
def index():
	return render_template("route.html")

# when request for stop list is sent
@app.route('/stops', methods=['POST'])
def sendStops():

	'''
	Zoe's Code
	'''

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