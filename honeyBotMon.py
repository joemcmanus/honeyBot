#!/usr/bin/python3
# File    : honeyBotMon.py - A script to alert on portscans and more
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

import RPi.GPIO as GPIO

import time
import argparse
import logging
import requests
import paho.mqtt.publish as pub
import os

parser = argparse.ArgumentParser(description='HoneyBot Log Monitor')
parser.add_argument('--pid', help="Create a pid file in /var/run/honeyBotMon.pid",  action="store_true")
parser.add_argument('--server', help="Server to send alerts to, default 127.0.0.1", default='127.0.0.1', type=str)
parser.add_argument('--log', help="Create a log file in /var/log/honeyBotMon.log",  action="store_true")
parser.add_argument('--relay', help="Which relay to activate, default 1", type=int, default=1, action="store")
parser.add_argument('--delay', help="Number of seconds to wait between readings, default 1", default=1, type=float, action="store")

args=parser.parse_args()


if args.pid:
	fh=open("/var/run/honeyBotMon.pid", "w")
	fh.write(str(os.getpid()))
	fh.close()

if args.log:
    logFile=args.log
    logging.basicConfig(filename='/var/log/honeyBotMon.log', level=logging.DEBUG)
    logging.debug("Started App")

def raiseAlert(relay):
	GPIO.output(relay,GPIO.HIGH)	
	time.sleep(5)
	GPIO.output(relay,GPIO.LOW)

def setPin(humanPin):
	if humanPin == 1:
		relay=26
	if humanPin == 2:
		relay=20
	if humanPin == 3:
		relay=21

	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(relay,GPIO.OUT)
	GPIO.output(relay,GPIO.LOW)
	
	return relay

def sendAlert(server, message):
	pub.single('honeyBot/IP', message, hostname=server)
	
relay=setPin(args.relay)

#open SSH failure log
sshFile=open("/var/log/auth.log")
sshFile.seek(0,2)
#open iptables log
iptablesFile=open("/var/log/iptables.log")
iptablesFile.seek(0,2)
#Cerate an empty dictionary for IPs
srcIPs={}

while(1):
	time.sleep(args.delay)	
	line=sshFile.readline()
	if line:
		if "sshd" in line and "closed" in line and "preauth" in line:
			srcIP=line.split()[8]
			print(srcIP)
			raiseAlert(relay)
			sendAlert(args.server, srcIP)

	line=iptablesFile.readline()
	if line:
		if "UDP" in line or "TCP" in line:
			for words in line.split():
				if "SRC" in words: 
					srcIP=words.split('=')[1]
				if "DPT" in words:
					dPort=words.split('=')[1]
			
			#count the number of ports keyed by src IP
			if srcIP:
				print("srcIP: {} dPort {}".format(srcIP, dPort))
				if srcIP not in srcIPs:
					srcIPs[srcIP] = 1 
				else:
					srcIPs[srcIP] += 1 

				if srcIPs[srcIP] == 4: 
					print("alert")
					raiseAlert(relay)	
					sendAlert(args.server, srcIP)
					srcIPs[srcIP] = 0 
					srcIP = None
