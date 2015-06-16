'''
Top left + bottom right corner of box -> filter stops by lat & long
mySQL db
'''

import urllib, zipfile, os, shutil, gtfs_parser, glob
from flask import jsonify, request
from app import app, db, models
from sets import Set
from datetime import datetime

@app.route('/agency/<dataset_id>', methods=['GET'])
def get_agency(dataset_id):
    url_args = request.args
    for key in url_args:
        print key + " : " + url_args[key]
    agencies = models.Agency.query.filter(models.Agency.dataset_id == dataset_id)
    return jsonify({ 'agencies' : [a.serialize() for a in agencies] })

@app.route('/stops/<dataset_id>', methods=['GET'])
def get_stops(dataset_id):
    stops = None
    trip_id = request.args.get('trip_id', '')
    if len(trip_id) == 0:
        stops = models.Stop.query.filter(models.Stop.dataset_id == dataset_id)
    else:
        trip = models.Trip.query.filter(models.Trip.dataset_id == dataset_id, models.Trip.trip_id == trip_id).first()
        if not trip is None:
            stops = trip.stops
        else:
            return jsonify({ '404' : 'No Stops Found' })
    return jsonify({ 'stops' : [s.serialize() for s in stops] })

@app.route('/routes/<dataset_id>', methods=['GET'])
def get_routes(dataset_id):
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
            start = request.args.get('start', '')
            stop = request.args.get('stop', '')
            
            if len(stop) > 0 and len(start) == 0:
                # the parameters provided cannot be used to filter, so return error
                return jsonify({ '404' : 'Cannot have end time without start time'}), 404
            elif len(start) == 0 and len(stop) == 0:
                # filter by latitude and longitude only
                stop_times = models.StopTime.query.filter(models.StopTime.stop_lon >= lon1, models.StopTime.stop_lon <= lon2, models.StopTime.stop_lat >= lat1, models.StopTime.stop_lat <= lat2, models.StopTime.dataset_id == dataset_id)
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
                    stop_times = models.StopTime.query.filter(models.StopTime.stop_lon >= lon1, models.StopTime.stop_lon <= lon2, models.StopTime.stop_lat >= lat1, models.StopTime.stop_lat <= lat2, models.StopTime.arrival_time >= start_time, models.StopTime.departure_time <= stop_time, models.StopTime.dataset_id == dataset_id)
                else:
                    # filter from initial time only
                    stop_times = models.StopTime.query.filter(models.StopTime.stop_lon >= lon1, models.StopTime.stop_lon <= lon2, models.StopTime.stop_lat >= lat1, models.StopTime.stop_lat <= lat2, models.StopTime.arrival_time >= start_time, models.StopTime.dataset_id == dataset_id)
                
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
        routes = models.Route.query.filter(models.Route.dataset_id == dataset_id)
        
    return jsonify({ 'routes' : [r.serialize(valid_trips, n) for r in routes] })
def array_from_query(q):
    a = []
    for item in q:
        a.append(item)
    return a
def unique_array(regular_array): # Order preserving
  seen = set()
  return [x for x in regular_array if x not in seen and not seen.add(x)]
  
@app.route('/trips/<dataset_id>', methods=['GET'])
def get_trips(dataset_id):
    trips = models.Trip.query.filter(models.Trip.dataset_id == dataset_id)
    return jsonify({ 'trips' : [t.serialize() for t in trips] })
    
@app.route('/comments/<dataset_id>', methods=['POST'])
def create_comment(dataset_id):
    trip_id = request.args.get('trip_id', '')
    text = request.args.get('text', '')
    if len(trip_id) == 0:
        return jsonify({ '404' : 'Must provide a Trip ID for the comment' })
    elif len(text) == 0:
        return jsonify({  '404' : 'Must provide text for the comment' })
    trip = models.Trip.query.filter(models.Trip.trip_id == trip_id, models.Trip.dataset_id == dataset_id).first()
    if trip is None:
        return jsonify({ '404' : 'Invalid Trip ID' })
    comment = models.Comment(text = text, dataset_id = dataset_id, trip = trip)
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.serialize()), 200

@app.route('/ratings/<dataset_id>', methods=['POST'])
def create_quality_rating(dataset_id):
    trip_id = request.args.get('trip_id', '')
    rating = request.args.get('rating', '')
    if len(trip_id) == 0:
        return jsonify({ '404' : 'Must provide a Trip ID for the rating' })
    elif len(rating) == 0:
        return jsonify({  '404' : 'Must provide a rating value' })
    trip = models.Trip.query.filter(models.Trip.trip_id == trip_id, models.Trip.dataset_id == dataset_id).first()
    if trip is None:
        return jsonify({ '404' : 'Invalid Trip ID' })
    quality_rating = models.QualityRating(rating = rating, dataset_id = dataset_id, trip = trip)
    db.session.add(quality_rating)
    db.session.commit()
    return jsonify(quality_rating.serialize()), 200
    
@app.route('/datapoints/<dataset_id>', methods=['POST'])
def create_datapoint(dataset_id):
    trip_id = request.args.get('trip_id', '')
    x = request.args.get('x', '')
    y = request.args.get('y', '')
    timestamp = datetime.utcnow()
    if len(trip_id) == 0:
        return jsonify({ '404' : 'Must provide a Trip ID for the datapoint' })
    elif len(x) == 0 or len(y) == 0:
        return jsonify({  '404' : 'Must provide x and y values' })
    trip = models.Trip.query.filter(models.Trip.trip_id == trip_id, models.Trip.dataset_id == dataset_id).first()
    if trip is None:
        return jsonify({ '404' : 'Invalid Trip ID' })
    datapoint = models.Datapoint(x = x, y = y, timestamp = timestamp, dataset_id = dataset_id, trip = trip)
    db.session.add(datapoint)
    db.session.commit()
    return jsonify(datapoint.serialize()), 200  

@app.route('/stop_times/<dataset_id>', methods=['GET'])
def get_stop_times(dataset_id):
    stop_times = models.StopTime.query.filter(models.StopTime.dataset_id == dataset_id)
    return jsonify({ 'stop_times' : [st.serialize() for st in stop_times] })

@app.route('/calendar/<dataset_id>', methods=['GET'])
def get_calendar(dataset_id):
    calendar = models.Calendar.query.filter(models.Calendar.dataset_id == dataset_id)
    return jsonify({ 'calendar' : [c.serialize() for c in calendar] })
    
@app.route('/calendar_dates/<dataset_id>', methods=['GET'])
def get_calendar_dates(dataset_id):
    cal_dates = models.CalendarDate.query.filter(models.CalendarDate.dataset_id == dataset_id)
    return jsonify({ 'calendar_dates' : [cd.serialize() for cd in cal_dates] })
    
@app.route('/shapes/<dataset_id>', methods=['GET'])
def get_shapes(dataset_id):
    shapes = None
    trip_id = request.args.get('trip_id', '')
    if len(trip_id) == 0:
        shapes = models.Shape.query.filter(models.Shape.dataset_id == dataset_id)
    else:
        trip = models.Trip.query.filter(models.Trip.trip_id == trip_id, models.Trip.dataset_id == dataset_id).first()
        if not trip is None:
            shapes = models.Shape.query.filter(models.Shape.shape_id == trip.shape_id, models.Shape.dataset_id == dataset_id)
        else:
            return jsonify({ '404' : 'Invalid Trip ID' })
    return jsonify({ 'shapes' : [s.serialize() for s in shapes] })    

@app.route('/load_gtfs', methods=['GET'])
def load_gtfs():
    delete_all_records()
    for file in glob.glob('*.zip'):
        zfile = zipfile.ZipFile(file)
        zfile.extractall('tmp/GTFS/')
        gtfs_parser.load_all(file.split('.')[0])
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
