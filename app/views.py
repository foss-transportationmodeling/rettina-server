'''
mySQL db?!?
'''

import urllib, zipfile, os, shutil, gtfs_parser, glob
from flask import jsonify, request
from app import app, db, models
from sets import Set
from datetime import datetime

def decode(url):
    return urllib.unquote(url).decode('utf8')

@app.route('/agency', methods=['GET'])
def get_agency():
    agencies = models.Agency.query.all()
    return jsonify({ 'agencies' : [a.serialize() for a in agencies] })

@app.route('/stops', methods=['GET'])
def get_stops():
    stops = None
    trip_id = decode(request.args.get('trip_id', ''))
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
    valid_trips = None
    n = 1
    try:
        n = int(request.args.get('next', 1))
    except ValueError:
        return jsonify({ '404' : 'Cannot parse \'next\' parameter'}), 404
    if len(request.args.keys()) > 0:
        # filter routes by the provided URL parameters
        lat1 = request.args.get('lat1', 999)
        lon1 = request.args.get('lon1', 999)
        lat2 = request.args.get('lat2', 999)
        lon2 = request.args.get('lon2', 999)
        if lat1 == 999 or lon1 == 999 or lat2 == 999 or lon2 == 999:
            # the parameters provided cannot be used to filter, so return error
            return jsonify({ '404' : 'Bad URL Parameters'}), 404
        else:
            stop_times = []
            start = decode(request.args.get('start', ''))
            stop = decode(request.args.get('stop', ''))
            
            if len(stop) > 0 and len(start) == 0:
                # the parameters provided cannot be used to filter, so return error
                return jsonify({ '404' : 'Cannot have end time without start time'}), 404
            elif len(start) == 0 and len(stop) == 0:
                # filter by latitude and longitude only
                stop_times = models.StopTime.query.filter(models.StopTime.stop_lon >= lon1, models.StopTime.stop_lon <= lon2, models.StopTime.stop_lat >= lat1, models.StopTime.stop_lat <= lat2)
            else:
                start_time = None
                stop_time = None
                try:
                    start_time = gtfs_parser.datetime_from_string(start)
                    if len(stop) > 0:
                        stop_time = gtfs_parser.datetime_from_string(stop)
                except:
                    return jsonify({ '404' : 'Cannot parse time'}), 404
                if not stop_time is None:
                    # filter within a range of time
                    stop_times = models.StopTime.query.filter(models.StopTime.stop_lon >= lon1, models.StopTime.stop_lon <= lon2, models.StopTime.stop_lat >= lat1, models.StopTime.stop_lat <= lat2, models.StopTime.arrival_time >= start_time, models.StopTime.departure_time <= stop_time)
                else:
                    # filter from initial time only
                    stop_times = models.StopTime.query.filter(models.StopTime.stop_lon >= lon1, models.StopTime.stop_lon <= lon2, models.StopTime.stop_lat >= lat1, models.StopTime.stop_lat <= lat2, models.StopTime.arrival_time >= start_time)
                
            stop_times = array_from_query(stop_times)
            stop_times.sort(key = lambda st: st.arrival_time, reverse = False)
            trips = []
            for stop_time in stop_times:
                trips.append(stop_time.trip)
            trips = unique_array(trips)
            
            filtered_routes = Set()
            for trip in trips:
                filtered_routes.add(trip.route)
            routes = filtered_routes
            valid_trips = trips
    else:
        # otherwise, no URL parameters are provided, so return all routes
        routes = models.Route.query.all()
        
    return jsonify({ 'routes' : [r.serialize(valid_trips, n) for r in routes] })
def array_from_query(q):
    a = []
    for item in q:
        a.append(item)
    return a
def unique_array(regular_array): # Order preserving
  seen = set()
  return [x for x in regular_array if x not in seen and not seen.add(x)]
  
@app.route('/trips', methods=['GET'])
def get_trips():
    trips = models.Trip.query.all()
    return jsonify({ 'trips' : [t.serialize() for t in trips] })
    
@app.route('/experiences', methods=['GET'])
def get_experiences():
    experiences = None
    trip_id = decode(request.args.get('trip_id', ''))
    route_id = decode(request.args.get('route_id', ''))
    if len(trip_id) == 0 and len(route_id) == 0:
        experiences = models.Experience.query.all()
    elif len(route_id) == 0:
        # only trip_id provided
        trip = models.Trip.query.filter(models.Trip.trip_id == trip_id).first()
        if trip is None:
            return jsonify({ '404' : 'Invalid Trip ID' })
        experiences = models.Experience.query.filter(models.Experience.trip == trip)
    else:
        # route_id provided (will take precedence over trip_id if both are provided)
        route = models.Route.query.filter(models.Route.route_id == route_id).first()
        if route is None:
            return jsonify({ '404' : 'Invalid Route ID' })
        experiences = models.Experience.query.filter(models.Experience.route == route)
    return jsonify({ 'experiences' : [e.serialize() for e in experiences] })
    
@app.route('/experiences', methods=['POST'])
def create_experience():
    trip_id = decode(request.args.get('trip_id', ''))
    comment = decode(request.args.get('comment', ''))
    quality = request.args.get('quality', -1)
    open_seats = request.args.get('open_seats', -1)
    if len(trip_id) == 0:
        return jsonify({ '404' : 'Must provide a Trip ID for the experience' })
    trip = models.Trip.query.filter(models.Trip.trip_id == trip_id).first()
    if trip is None:
        return jsonify({ '404' : 'Invalid Trip ID' })
    experience = models.Experience(comment = comment, quality = quality, open_seats = open_seats, trip = trip, route = trip.route)
    db.session.add(experience)
    db.session.commit()
    experience.experience_id = str(experience.id) # the object's ID isn't set until it is added to the DB
    db.session.add(experience)
    db.session.commit()
    return jsonify(experience.serialize()), 200
    
@app.route('/locations', methods=['GET'])
def get_locations():
    locations = None
    trip_id = decode(request.args.get('trip_id', ''))
    route_id = decode(request.args.get('route_id', ''))
    if len(trip_id) == 0 and len(route_id) == 0:
        locations = models.Location.query.all()
    elif len(route_id) == 0:
        # only trip_id provided
        trip = models.Trip.query.filter(models.Trip.trip_id == trip_id).first()
        if trip is None:
            return jsonify({ '404' : 'Invalid Trip ID' })
        locations = models.Location.query.filter(models.Location.trip == trip)
    else:
        # route_id provided (will take precedence over trip_id if both are provided)
        route = models.Route.query.filter(models.Route.route_id == route_id).first()
        if route is None:
            return jsonify({ '404' : 'Invalid Route ID' })
        locations = models.Location.query.filter(models.Location.route == route)
    return jsonify({ 'locations' : [l.serialize() for l in locations] })
    
@app.route('/locations', methods=['POST'])
def create_locations():
    locations = []
    
    json = request.get_json()
    if json is None:
        return jsonify({ '404' : 'Unable to parse JSON. Did you specify a content type of \'application/json\'?' })
        
    trip_id = None
    try:
        trip_id = json['trip_id']
    except KeyError:
        return jsonify({ '404' : 'Must provide a Trip ID' })
    trip = models.Trip.query.filter(models.Trip.trip_id == trip_id).first()
    if trip is None:
        return jsonify({ '404' : 'Invalid Trip ID' })
        
    locs = None
    try:
        locs = json['locations']
    except KeyError:
        return jsonify({ '404' : 'Must provide locations' })
    for loc in locs:
        try:
            l = models.Location(x = loc['x'], y = loc['y'], timestamp = datetime.utcnow(), trip = trip, route = trip.route)
            db.session.add(l)
            locations.append(l)
        except KeyError:
            return jsonify({ '404' : 'An x or y value is missing from one of the locations' })
    db.session.commit()
    for l in locations:
        l.location_id = str(l.id) # the object's ID isn't set until it is added to the DB
        db.session.add(l)
    db.session.commit()
    return jsonify({ 'locations' : [l.serialize() for l in locations] }), 200
    
@app.route('/stop_times', methods=['GET'])
def get_stop_times():
    stop_times = models.StopTime.query.all()
    return jsonify({ 'stop_times' : [st.serialize() for st in stop_times] })

@app.route('/calendar', methods=['GET'])
def get_calendar():
    calendar = models.Calendar.query.all()
    return jsonify({ 'calendar' : [c.serialize() for c in calendar] })
    
@app.route('/calendar_dates', methods=['GET'])
def get_calendar_dates():
    cal_dates = models.CalendarDate.query.all()
    return jsonify({ 'calendar_dates' : [cd.serialize() for cd in cal_dates] })
    
@app.route('/shapes', methods=['GET'])
def get_shapes():
    shapes = None
    trip_id = decode(request.args.get('trip_id', ''))
    if len(trip_id) == 0:
        shapes = models.Shape.query.all()
    else:
        trip = models.Trip.query.filter(models.Trip.trip_id == trip_id).first()
        if not trip is None:
            if 'UConn' in trip.trip_id:
                s_id = trip.route.route_id
                shapes = models.Shape.query.filter(models.Shape.shape_id == s_id)
            else:
                shapes = models.Shape.query.filter(models.Shape.shape_id == trip.shape_id)
        else:
            return jsonify({ '404' : 'Invalid Trip ID' })
    return jsonify({ 'shapes' : [s.serialize() for s in shapes] })    

@app.route('/load_gtfs', methods=['GET'])
def load_gtfs():
    delete_all_records()
    for file in glob.glob('*.zip'):
        zfile = zipfile.ZipFile(file)
        zfile.extractall('tmp/GTFS/')
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
    ex = models.Experience.query.delete()
    loc = models.Location.query.delete()
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
