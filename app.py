from flask import Flask, render_template, request
from urllib2 import Request, urlopen, URLError
import json
from datetime import datetime
import arrow
import requests

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/graph', methods=['GET', 'POST'])
def graph(chartID = 'chart_ID', chart_type = 'line', chart_height = 500):
	company = 'Dropbox'
	if request.method == 'POST':
		company = request.form['company']
	x, y, name = list_org(str(company))
	chart = {'renderTo': chartID, 'type': chart_type, 'height': chart_height}
	series = [{'name': name, 'data': y}]
	pageType = 'graph'
	title = {'text': 'Investments'}
	xAxis = {"categories": x}
	yAxis = {'title': {'text':'$ Amount'}}
	return render_template('graph.html', pageType=pageType, chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis, yAxis=yAxis)

def list_org(name):
	request = Request('https://api.crunchbase.com/v/2/organization/'+ name +'?user_key=16d77982a401bdb3f2a784ee5329038b')
	x = []
	y = []

	try:
		response = urlopen(request)
		org = json.loads(response.read())
		for item in org['data']['relationships']['funding_rounds']['items']:
			uuid = item['path'].replace('funding-round/', '')
			x.append(list_funding_round(uuid)[0])
			y.append(list_funding_round(uuid)[1])

	except URLError as e:
		print 'No Org', e

	xy = zip(x,y)
	xy.sort()

	x = [x[0] for x in xy]
	y = [y[1] for y in xy]

	return x, y, name

def list_funding_round(uuid):
	request = Request('https://api.crunchbase.com/v/2/funding-round/'+uuid+'?user_key=16d77982a401bdb3f2a784ee5329038b')
	try:
		response = urlopen(request)
		funding_round = json.loads(response.read())
		funding_type = funding_round['data']['properties']['funding_type']
		money_raised_usd = (funding_round['data']['properties']['money_raised_usd'])
		announced_on = (funding_round['data']['properties']['announced_on'])
		announced_on = arrow.get(announced_on)
		announced_on = announced_on.format('YYYY-MM-DD')

		return announced_on, money_raised_usd

		try:
			series = funding_round['data']['properties']['series']
		except:
			pass

	except URLError as e:
		print 'No Funding Round', e
		pass

if __name__=='__main__':
	app.run(debug=True)
	
	
