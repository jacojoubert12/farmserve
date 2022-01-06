# Farmserve

Server side code for Farmview and Farmact repos.

farmserve_websockets.py collects sensor data and store it in InfluxDB
app.py is a Flask API to receive instructions from farview and forward them to farmact
