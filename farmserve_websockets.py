#!/usr/bin/env python3

#import pymongo
from simple_websocket_server import WebSocketServer, WebSocket
import threading
from threading import Event
import time
import datetime
import pytz
import json
from influxdb import InfluxDBClient

ws_clients = []


class THWebSocket(WebSocket):

    def __init__(self, server, sock, address):
        WebSocket.__init__(self, server, sock, address)
        self.db_client = InfluxDBClient(host='68.183.44.212', port=8086)
        self.db_client.create_database('farm_iot_sensor_data')
        self.db_client.switch_database('farm_iot_sensor_data')
        self.is_listener = False

    def get_db_entry_json(self, node, temperature, humidity, soil_moisture):
        db_entry_data = [{
            "measurement" : "temperature_humidity",
            "tags": {
              "node_id" : node
            },
            "fields" : {
              "Temperature" : temperature,
              "Humidity" : humidity,
              "Soil Moisture" : soil_moisture
            }
        }]

        return db_entry_data

    def handle(self):
        SAST = pytz.timezone('Africa/Johannesburg')
        ct = datetime.datetime.now(SAST)
        print(ct, self.data)
        #client.send_message(self.data)
        self.send_message(self.data)
        print(self.data)
        if "_id" in self.data and "temperature" in self.data:
            datajson = json.loads(self.data)
            self.node_id = datajson['node_id']
            t = datajson['temperature']
            h = datajson['humidity']
            m = datajson['soil_moisture']
            self.db_client.write_points(self.get_db_entry_json(self.node_id, t, h, m))

        if "_id" in self.data and "cam_ready" in self.data:
            datajson = json.loads(self.data)
            self.node_id = datajson['node_id']
            cam_ready = datajson['cam_ready']
            ip = datajson['ip']
            print("Cam Ready:", cam_ready, "IP:", ip)
        
            if cam_ready == 1:
                for client in ws_clients: #Forward data to pic listener
                    if client.is_listener:
                        client.send_message(self.data)
                        #client.send_message("Cam ready for %s IP: %s" % (self.node_id, ip))

        if "_id" in self.data and "pic_listener" in self.data:
            print("Pic Listener registered")
            self.is_listener = True

        #for client in ws_th_clients: #Forward data web Trainers
        #    if client != self:
        #        client.send_message(self.data)
 
        #for client in ws_th_clients: #Forward data to web clients
        #    if client.node_id is None:
        #        print("A Web client is connected, sending:")
        #        client.send_message(self.data)

    def connected(self):
        print(self.address, 'Client Connected')
        ws_clients.append(self)

    def handle_close(self):
        print(self.address, 'Client Closed')
        ws_clients.remove(self)

class THWebSocketThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stopped =  Event()

    def run(self):
        server = WebSocketServer('68.183.44.212', 12012, THWebSocket)
        #server = WebSocketServer('localhost', 12012, THWebSocket)
        print("Serving ws @ 68.183.44.212:12012")
        #print("Serving ws @ localhost:12012")
        server.serve_forever()


def main():
    THThread = THWebSocketThread()
    THThread.daemon = True
    THThread.start()

    print("Wating for clients to connect...")

    while(1):
        time.sleep(2)

if __name__ == "__main__":
    main()
