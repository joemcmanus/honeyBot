#!/usr/bin/python3
# File    : honeyBot.py - A script to alert on portscans and more
# Author  : Joe McManus josephmc@alumni.cmu.edu
# Version : 0.1 04/01/2019
# Copyright (C) 2019 Joe McManus

import RPi.GPIO as GPIO

import time
import argparse
import logging
#import requests

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

relay=setPin(args.relay)

#open SSH failure log
sshFile=open("/var/log/auth.log")
sshFile.seek(0,2)
#open iptables log
iptablesFile=open("/var/log/iptables.log")
iptablesFile.seek(0,2)
#Cerate an empty dictionary for 
srcIPs={}

while(1):
	time.sleep(args.delay)	
	line=sshFile.readline()
	if line:
		if "sshd" in line and "closed" in line and "preauth" in line:
			raiseAlert(relay)

	ipLine=iptablesFile.readline()
	if ipLine:
		lineData=ipLine.split()
		#read UDP
		if len(lineData) == 22:
			srcIP=lineData[11].split('=')[1]
			dPort=lineData[20].split('=')[1]
		#read TCP 	
		if len(lineData) == 26:
			srcIP=lineData[11].split('=')[1]
			dPort=lineData[21].split('=')[1]
			
		#count the number of ports keyed by src IP
		if srcIP:
			if srcIP not in srcIPs:
				srcIPs[srcIP] = 1 
			else:
				srcIPs[srcIP] += 1 

			if srcIPs[srcIP] == 4: 
				raiseAlert(relay)	
				srcIPs[srcIP] = 0 
				srcIP = None
