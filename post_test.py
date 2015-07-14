import urllib, json

url = 'localhost:5000/locations'

data = {
	'trip_id' : '1 UConn Transportation Service',
	'locations' :
	[
		{
			'x' : 1,
			'y' : 2,
			'timestamp' : 'Nov 30 2010 9:20:37AM',
			'location_technology' : 'Samsung Galaxy S6'
		},
		{
			'x' : 4,
			'y' : 10,
			'timestamp' : 'Jun 1 2015 10:00:00PM',
			'location_technology' : 'Motorola Moto X'
		},
		{
			'x' : 37.1,
			'y' : 20.2,
			'timestamp' : 'Aug 12 2012 4:30:00AM',
			'location_technology' : 'LG G4'
		}
	]
}

req = urllib2.Request(url)
req.add_header('Content-Type', 'application/json')

response = urllib2.urlopen(req, json.dumps(data))

print response