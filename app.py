from flask import Flask, jsonify, request
from flask_cors import CORS

import requests

app = Flask(__name__)
CORS(app=app)

@app.route("/")
def control_water_channels():
    channel = int(request.args.get('channel'))
    duration = int(request.args.get('duration'))
    on = request.args.get('on')
    print(channel, duration, on)
    payload = {"channel":channel, "duration":duration, "on":on}
    r = requests.get('http://10.8.0.3:5000/', params=payload)
    print(r)

    return "Done"
