from app import db, models
from time import strptime
from datetime import datetime
from pytz import utc
from calendar import timegm

GTFS_PATH = "tmp/GTFS/"

def object_for_name(name):
    if name == "Agency":
        return models.Agency()
    elif name == "Stop":
        return models.Stop()
    elif name == "Route":
        return models.Route()
    elif name == "Trip":
        return models.Trip()
    elif name == "StopTime":
        return models.StopTime()
    elif name == "Calendar":
        return models.Calendar()
    elif name == "CalendarDate":
        return models.CalendarDate()
    elif name == "Shape":
        return models.Shape()
    else:
        return None
        
def load_objects(file, name):
    objects = []
    f = open(file, 'r')
    dataset_id = file.split('.')[0]
    clean_first_line = f.readline().strip().replace(' ', '')
    keys = clean_first_line.split(',')
    try:
        for line in f:
            obj = object_for_name(name)
            values = line.strip().split(',')
            if len(values) == 0:
                continue
            for i, key in enumerate(keys):
                value = values[i].strip()
                # handle special cases for setting relationships
                if name == "StopTime" and key == "trip_id":
                    set_trip_for_stop_time(obj, value)
                elif name == "StopTime" and key == "arrival_time":
                    obj.arrival_time = datetime_from_string(value)
                elif name == "StopTime" and key == "departure_time":
                    obj.departure_time = datetime_from_string(value)
                elif name == "StopTime" and key == "stop_id":
                    set_stop_for_stop_time(obj, value)
                elif name == "Route" and key == "agency_id":
                    set_agency_for_route(obj, value)
                elif name == "Trip" and key == "route_id":
                    set_route_for_trip(obj, value)
                else:
                    if hasattr(obj, key):
                        setattr(obj, key, value)
            obj.dataset_id = dataset_id
            objects.append(obj)
    except IndexError:
        print "A value is missing from " + file
    return objects
    
def datetime_from_string(string):
    hr = int(string.split(":")[0])
    if hr >= 24:
        l = list(string)
        l[0] = "0"
        l[1] = str(hr % 24)
        string = "".join(l)
    def to_datetime_from_utc(time_tuple):
        timestamp = timegm(time_tuple)
        if hr >= 24:
            timestamp  = timestamp + 24*60*60
        return datetime.fromtimestamp(timegm(time_tuple), tz = utc)    
    return to_datetime_from_utc(strptime(string, "%H:%M:%S"))

# this will always happen before setting the Stop ID for a stop_time
# due to the ordering of trip_id and stop_id in GTFS
def set_trip_for_stop_time(stop_time, trip_id):
    trip = models.Trip.query.filter(models.Trip.trip_id == trip_id).first()
    if not trip is None:
        stop_time.trip = trip
        
def set_stop_for_stop_time(stop_time, stop_id):
    stop = models.Stop.query.filter(models.Stop.stop_id == stop_id).first()
    if not stop is None:
        stop_time.stop = stop
        stop_time.stop_lat = stop.stop_lat
        stop_time.stop_lon = stop.stop_lon
        # a stop_time's trip must be set before its stop,
        # in order to link trips to stops
        trip = stop_time.trip
        if not trip is None:
            trip.stops.append(stop)
            
def set_agency_for_route(route, agency_id):
    agency = models.Agency.query.filter(models.Agency.agency_id == agency_id).first()
    if not agency is None:
        route.agency = agency

def set_route_for_trip(trip, route_id):
    route = models.Route.query.filter(models.Route.route_id == route_id).first()
    if not route is None:
        trip.route = route

def commit_objects(objects):
    for obj in objects:
        db.session.add(obj)
    db.session.commit()

def load_agency():
    print "loading agencies"
    try:
        agencies = load_objects(GTFS_PATH + "agency.txt", "Agency")
        commit_objects(agencies)
    except:
        print "Error in loading agency.txt"
        db.session.rollback()
        
def load_stops():
    print "loading stops"
    try:
        stops = load_objects(GTFS_PATH + "stops.txt", "Stop")
        commit_objects(stops)
    except:
        print "Error in loading stops.txt"
        db.session.rollback()
        
def load_routes():
    print "loading routes"
    try:
        routes = load_objects(GTFS_PATH + "routes.txt", "Route")
        commit_objects(routes)
    except:
        print "Error in loading routes.txt"
        db.session.rollback()
        
def load_trips():
    print "loading trips"
    try:
        trips = load_objects(GTFS_PATH + "trips.txt", "Trip")
        commit_objects(trips)
    except:
        print "Error in loading trips.txt"
        db.session.rollback()
        
def load_stop_times():
    print "loading stop_times"
    try:
        stop_times = load_objects(GTFS_PATH + "stop_times.txt", "StopTime")
        commit_objects(stop_times)
    except:
        print "Error in loading stop_times.txt"
        db.session.rollback()
        
def load_calendar():
    print "loading calendar"
    try:
        calendar = load_objects(GTFS_PATH + "calendar.txt", "Calendar")
        commit_objects(calendar)
    except:
        print "Error in loading calendar.txt"
        db.session.rollback()
        
def load_calendar_dates():
    print "loading calendar dates"
    try:
        calendar_dates = load_objects(GTFS_PATH + "calendar_dates.txt", "CalendarDate")
        commit_objects(calendar_dates)
    except:
        print "Error in loading calendar_dates.txt"
        db.session.rollback()
        
def load_shapes():
    print "loading shapes"
    try:
        shapes = load_objects(GTFS_PATH + "shapes.txt", "Shape")
        commit_objects(shapes)
    except:
        print "Error in loading shapes.txt"
        db.session.rollback()

def load_all():
    # the order is important (necessary for relationships):
    # agencies must be loaded before routes
    load_agency()
    # routes must be loaded before trips and before shapes
    load_routes()
    # trips must be loaded before stop_times
    load_trips()
    # stops must be loaded before stop_times 
    load_stops()
    load_stop_times()
    load_calendar()
    load_calendar_dates()
    load_shapes()


