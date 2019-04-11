#!/usr/bin/env python3
# File    : honeyWeb.py - Web Front end to the HoneyBot
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
import sqlite3

parser = argparse.ArgumentParser(description='HoneyWeb HoneyBot Web Front End')
parser.add_argument('--pid', help="Create a pid file in /var/run/honeyMqtt.pid",  action="store_true")
parser.add_argument('--dbPath', help=" Location of honeyBot.sql3 sqlite db file, defaults to pwd", action="store")
parser.add_argument('--host', help="IP to listen on, defaults to 0.0.0.0", default='0.0.0.0',  action="store")

args=parser.parse_args()
if args.dbPath: 
	dbFile=args.dbPath + "/honeyBot.sql3"
else:
	dbFile='honeyBot.sql3'


if args.pid:
	fh=open("/var/run/honeyWeb.pid", "w")
	fh.write(str(os.getpid()))
	fh.close()

try:
	from flask import Flask, render_template, Markup, request, redirect, make_response, send_file
except:
	print("ERROR: Missing flask, make sure it is installed.\nTRY: pip install flask")

app = Flask(__name__)

@app.route('/')
def index():
	db = sqlite3.connect(dbFile)
	cursor=db.cursor()
	query='select ip, dateStamp from honeyLog'
	cursor.execute(query)
	results=''
	rows=cursor.fetchall()
	for row in rows:
		results=results +  Markup("\n" +row[0] + " " + row[1] + "<br>")
	query='select count(ip), ip from honeyLog group by ip'
	cursor.execute(query)
	rows=cursor.fetchall()
	for row in rows:
		results=results + Markup( "\n" +str(row[0]) + " " + row[1]+ "<br>" )
	
	bodyText=results 
	return render_template('template.html', bodyText=bodyText)

if __name__ == '__main__':
	app.run(host=args.host, port=443, ssl_context = 'adhoc')
