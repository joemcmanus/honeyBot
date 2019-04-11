#!/usr/bin/python3
# File    : honeyMqtt.py - Program to listen for MQTT events
# Author  : Joe McManus josephmc@alumni.cmu.edu
# Version : 0.1 04/01/2019
# Copyright (C) 2019 Joe McManus

import argparse
import paho.mqtt.client as paho
import sqlite3
import datetime

parser = argparse.ArgumentParser(description='HoneyMQTT Event Monitor')
parser.add_argument('--pid', help="Create a pid file in /var/run/honeyMqtt.pid",  action="store_true")

args=parser.parse_args()

if args.pid:
	fh=open("/var/run/honeyMqtt.pid", "w")
	fh.write(str(os.getpid()))
	fh.close()


def on_message(mosq, userdata, msg):
	print(msg.payload.decode("utf-8"))
	now=datetime.datetime.now()
	t=(msg.payload.decode("utf-8"),now,)
	query='insert into honeyLog(ip, dateStamp) values(?,?)'
	cursor=db.cursor()
	cursor.execute(query, t)
	db.commit()
	
	

db = sqlite3.connect('honeyBot.sql3')
db.row_factory = sqlite3.Row


mqtt=paho.Client()
mqtt.on_message = on_message
mqtt.connect("localhost", 1883, 60)
mqtt.subscribe("honeyBot/+", 0)
mqtt.loop_forever()
