'''
Top left + bottom right corner of box -> filter stops by lat & long
mySQL db
'''

import urllib, zipfile, os, shutil, gtfs_parser
from flask import jsonify, request
from app import app, db, models
from sets import Set

@app.route('/agency', methods=['GET'])
def get_agency():
    url_args = request.args
    for key in url_args:
        print key + " : " + url_args[key]
    agencies = models.Agency.query.all()
    return jsonify({ 'agencies' : [a.serialize() for a in agencies] })

@app.route('/stops', methods=['GET'])
def get_stops():
    stops = models.Stop.query.all()
    return jsonify({ 'stops' : [s.serialize() for s in stops] })

@app.route('/routes', methods=['GET'])
def get_routes():
    routes = models.Route.query.all()
    if len(request.args.keys()) > 0:
        # filter routes by the provided URL parameters
        lat1 = request.args.get('lat1', 999)
        lon1 = request.args.get('lon1', 999)
        lat2 = request.args.get('lat2', 999)
        lon2 = request.args.get('lon2', 999)
        time = request.args.get('time', '')
        invalid = lat1 == 999 or lon1 == 999 or lat2 == 999 or lon2 == 999
        if not invalid:
            stop_times = []
            if len(time) > 0:
                # filter by latitude, longitude, and time
                stop_times = models.StopTime.query.filter(models.StopTime.stop_lon >= lon1, models.StopTime.stop_lon <= lon2, models.StopTime.stop_lat >= lat1, models.StopTime.stop_lat <= lat2, models.StopTime.arrival_time == time)
            else:
                # filter by latitude and longitude only
                stop_times = models.StopTime.query.filter(models.StopTime.stop_lon >= lon1, models.StopTime.stop_lon <= lon2, models.StopTime.stop_lat >= lat1, models.StopTime.stop_lat <= lat2)
            trip_ids = Set()
            for stop_time in stop_times:
                trip_ids.add(stop_time.trip_id)
            all_trips = models.Trip.query.all()
            route_ids = Set()
            for trip in all_trips:
                if trip.trip_id in trip_ids:
                    route_ids.add(trip.route_id)
            filtered_routes = []
            for route in routes:
                if route.route_id in route_ids:
                    filtered_routes.append(route)
            routes = filtered_routes
        else:
            # the parameters provided cannot be used to filter, so return error
            return jsonify({ '404' : 'Bad URL Parameters'}), 404
    # otherwise, no URL parameters are provided, so return all routes
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
    shapes = models.Shape.query.all()
    return jsonify({ 'shapes' : [s.serialize() for s in shapes] })    

@app.route('/load_gtfs', methods=['GET'])
def load_gtfs():
    zfile = zipfile.ZipFile('UC_GTFS.zip')
    zfile.extractall('tmp/GTFS/')
    delete_all_records()
    gtfs_parser.load_all()
    shutil.rmtree('tmp/GTFS')
    return jsonify({})
def delete_all_records():
    a = models.Agency.query.all()
    cd = models.CalendarDate.query.all()
    c = models.Calendar.query.all()
    r = models.Route.query.all()
    st = models.StopTime.query.all()
    s = models.Stop.query.all()
    t = models.Trip.query.all()
    sh = models.Shape.query.all()
    for array in [a, cd, c, r, st, s, t, sh]:
        for item in array:
            db.session.delete(item)
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
