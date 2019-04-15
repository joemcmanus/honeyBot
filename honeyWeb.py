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
import os
import plotly
import pandas as pd
import plotly.graph_objs as go

parser = argparse.ArgumentParser(description='HoneyWeb HoneyBot Web Front End')
parser.add_argument('--pid', help="Create a pid file in /var/run/honeyMqtt.pid",  action="store_true")
parser.add_argument('--dbPath', help=" Location of honeyBot.sql3 sqlite db file, defaults to /var/honeyBot", action="store")
parser.add_argument('--host', help="IP to listen on, defaults to 0.0.0.0", default='0.0.0.0',  action="store")

args=parser.parse_args()
if args.dbPath: 
	dbFile=args.dbPath + "/honeyBot.sql3"
else:
	dbFile='/var/honeyBot/honeyBot.sql3'


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
	query='select count(ip)as ipCount , ip, country from honeyLog group by ip order by ipCount desc'
	cursor.execute(query)
	bodyText=Markup(''' <br><center> <table> <tr colspan=3 callpadding=2> 
			<td bgcolor=black>><font color=white><b>Count</b></font></td>
			<td bgcolor=black>><font color=white><b>IP</b></font></td>
			<td bgcolor=black>><font color=white><b>Location</b></font></td>
			</tr>''')
	rows=cursor.fetchall()
	results=''
	for count, ip, country  in rows:
		results=results+ Markup('<tr> <td> ' + str(count) + '</td> <td> ' + ip + '</td><td> ' + country + '</td></tr>\n')
	titleText="HoneyBot Attacks"
	bodyText=bodyText + results + Markup("</table> </center>")

	cursor=db.cursor()
	query='select count(ip), country from honeyLog group by country'
	cursor.execute(query)
	rows=cursor.fetchall()
	countries=[]
	attackCount=[]
	for count, country in rows:
		countries.append(country)
		attackCount.append(count)

	countries= pd.Series(countries)
	countryCount= pd.Series(attackCount) 
	df = pd.DataFrame({"Country": countries , "Attack Count": attackCount}) 

	data = [go.Choropleth(
		locations= df['Country'],
		z = df['Attack Count'],
		text = df['Country'],
		locationmode = 'country names',
		colorscale = [
        		[0, "rgb(5, 10, 172)"],
	        	[0.1, "rgb(40, 60, 190)"],
       		 	[0.2, "rgb(70, 100, 245)"],
       		 	[0.3, "rgb(90, 120, 245)"],
       		 	[0.4, "rgb(106, 137, 247)"],
      	 	 	[0.8, "rgb(220, 220, 220)"]
    		],
		autocolorscale = False,
		reversescale = True,
		marker = go.choropleth.Marker(
			line = go.choropleth.marker.Line(
				color = 'rgb(180,180,180)',
				width = 0.5
			)),
		colorbar = go.choropleth.ColorBar(
			tickprefix = '',
			title = 'Attacks'),
	)]

	layout = go.Layout(
		title = go.layout.Title(
			text = 'Attack Traffic'
		),
		geo = go.layout.Geo(
			showframe = True,
			showcoastlines = True,
			projection = go.layout.geo.Projection(
				type = 'equirectangular'
			)
		),
		annotations = [go.layout.Annotation(
			x = 0.55,
			y = 0.1,
			xref = 'paper',
			yref = 'paper',
			text = 'Source: <a href=https://github.com/joemcmanus/honeyBot> HoneyBot </a>',
			showarrow = False
		)]
	)

	fig = go.Figure(data = data, layout = layout)
	mapDiv=Markup(plotly.offline.plot(fig, output_type='div'))
	return render_template('template.html', bodyText=bodyText, titleText=titleText, mapDiv=mapDiv)

@app.route('/about')
def about():
	titleText="About"
	bodyText=Markup('''This application is a fun way to visulize network attacks in the real world.
	<br>
	Written by Joe McManus josephmc@alumni.cmu.edu and released under the GPL. Copywrite Joe McManus 2019 <br>
	''')
	return render_template('template.html', bodyText=bodyText, titleText=titleText)

if __name__ == '__main__':
	app.run(host=args.host, debug=True, port=443, ssl_context = 'adhoc', threaded=True)
