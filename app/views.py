'''
Top left + bottom right corner of box -> filter stops by lat & long
mySQL db
'''

import urllib, zipfile, os, shutil, gtfs_parser
from flask import jsonify, request, send_from_directory
from app import app, db, models
from sets import Set

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path + ".json")

@app.route('/agency', methods=['GET'])
def get_agency():
    url_args = request.args
    for key in url_args:
        print key + " : " + url_args[key]
    agencies = models.Agency.query.all()
    return jsonify({ 'agencies' : [a.serialize() for a in agencies] })

@app.route('/stops', methods=['GET'])
def get_stops():
    stops = None
    trip_id = request.args.get('trip_id', '')
    if len(trip_id) == 0:
        stops = models.Stop.query.all()
    else:
        trip = models.Trip.query.filter(models.Trip.trip_id == trip_id).first()
        if not trip is None:
            stops = trip.stops
        else:
            return jsonify({ '404' : 'No Stops Found' })
    return jsonify({ 'stops' : [s.serialize() for s in stops] })

@app.route('/routes', methods=['GET'])
def get_routes():
    routes = None
    if len(request.args.keys()) > 0:
        # filter routes by the provided URL parameters
        lat1 = request.args.get('lat1', 999)
        lon1 = request.args.get('lon1', 999)
        lat2 = request.args.get('lat2', 999)
        lon2 = request.args.get('lon2', 999)
        time = request.args.get('time', '')
        invalid = lat1 == 999 or lon1 == 999 or lat2 == 999 or lon2 == 999
        if invalid:
            # the parameters provided cannot be used to filter, so return error
            return jsonify({ '404' : 'Bad URL Parameters'}), 404
        else:
            stop_times = []
            if len(time) > 0:
                # filter by latitude, longitude, and time
                stop_times = models.StopTime.query.filter(models.StopTime.stop_lon >= lon1, models.StopTime.stop_lon <= lon2, models.StopTime.stop_lat >= lat1, models.StopTime.stop_lat <= lat2, models.StopTime.arrival_time == time)
            else:
                # filter by latitude and longitude only
                stop_times = models.StopTime.query.filter(models.StopTime.stop_lon >= lon1, models.StopTime.stop_lon <= lon2, models.StopTime.stop_lat >= lat1, models.StopTime.stop_lat <= lat2)
            trips = Set()
            for stop_time in stop_times:
                trips.add(stop_time.trip)
            filtered_routes = Set()
            for trip in trips:
                filtered_routes.add(trip.route)
            routes = filtered_routes
    else:
        # otherwise, no URL parameters are provided, so return all routes
        routes = models.Route.query.all()
    return jsonify({ 'routes' : [r.serialize() for r in routes] })

@app.route('/trips', methods=['GET'])
def get_trips():
    trips = models.Trip.query.all()
    return jsonify({ 'trips' : [t.serialize() for t in trips] })

@app.route('/stop_times', methods=['GET'])
def get_stop_times():
    stop_times = models.StopTime.query.all()
    return jsonify({ 'stop_times' : [st.serialize() for st in stop_times] })

@app.route('/calendar', methods=['GET'])
def get_calendar():
    calendar = models.Calendar.query.filter(models.Calendar.friday == 1, models.Calendar.end_date == "20150509")
    return jsonify({ 'calendar' : [c.serialize() for c in calendar] })
    
@app.route('/calendar_dates', methods=['GET'])
def get_calendar_dates():
    cal_dates = models.CalendarDate.query.all()
    return jsonify({ 'calendar_dates' : [cd.serialize() for cd in cal_dates] })
    
@app.route('/shapes', methods=['GET'])
def get_shapes():
    shapes = None
    trip_id = request.args.get('trip_id', '')
    if len(trip_id) == 0:
        shapes = models.Shape.query.all()
    else:
        trip = models.Trip.query.filter(models.Trip.trip_id == trip_id).first()
        if not trip is None and not trip.route is None:
            shapes = trip.route.shapes
        else:
            return jsonify({ '404' : 'No Shapes Found' })
    return jsonify({ 'shapes' : [s.serialize() for s in shapes] })    

@app.route('/load_gtfs', methods=['GET'])
def load_gtfs():
    zfile = zipfile.ZipFile('UC_GTFS.zip')
    zfile.extractall('tmp/GTFS/')
    delete_all_records()
    gtfs_parser.load_all()
    shutil.rmtree('tmp/GTFS')
    return jsonify({ '200' : 'Data Loaded' })
def delete_all_records():
    a = models.Agency.query.delete()
    cd = models.CalendarDate.query.delete()
    c = models.Calendar.query.delete()
    r = models.Route.query.delete()
    st = models.StopTime.query.delete()
    s = models.Stop.query.delete()
    t = models.Trip.query.delete()
    sh = models.Shape.query.delete()
    db.session.commit()
    
@app.errorhandler(400)
def bad_request(error):
    return jsonify({ '400' : 'Bad Request' }), 400  
    
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({ '404' : 'Not Found Error' }), 404 
    
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({ '500' : 'Internal Server Error' }), 500
