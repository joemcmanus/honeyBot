#!/usr/bin/env python3
# File    : honeyMqtt.py - Program to listen for MQTT events
# Author  : Joe McManus josephmc@alumni.cmu.edu
# Version : 0.1 04/01/2019
# Copyright (C) 2019 Joe McManus

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import paho.mqtt.client as paho
import sqlite3
import datetime
import os

parser = argparse.ArgumentParser(description='HoneyMQTT Event Monitor')
parser.add_argument('--pid', help="Create a pid file in /var/run/honeyMqtt.pid",  action="store_true")
parser.add_argument('--dbPath', help="Create a sqlite db file in specified path, defaults to /var/honeyBot", action="store")

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
	
	
if args.dbPath: 
	dbFile=args.dbPath + "/honeyBot.sql3"
else:
	dbFile='/var/honeyBot/honeyBot.sql3'

db = sqlite3.connect(dbFile)
db.row_factory = sqlite3.Row


mqtt=paho.Client()
mqtt.on_message = on_message
mqtt.connect("localhost", 1883, 60)
mqtt.subscribe("honeyBot/+", 0)
mqtt.loop_forever()
