from app import db, models
from time import strptime
from datetime import datetime
from pytz import utc
from calendar import timegm

import thread

IDS = ["stop_id", "route_id", "service_id", "trip_id", "shape_id"]

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
        
AGENCY_ID = ""
        
def load_objects(file, name, agency_id = None):
    objects = []
    f = open(file, 'r')
    clean_first_line = f.readline().strip().replace(' ', '')
    keys = clean_first_line.split(',')
    global AGENCY_ID
    if not agency_id is None:
        AGENCY_ID = agency_id
    try:
        for line in f:
            obj = object_for_name(name)
            values = line.strip().split(',')
            if len(values) == 0:
                continue
            for i, key in enumerate(keys):
                value = values[i].strip()
                if name == "Agency" and key == "agency_name":
                    AGENCY_ID = " " + value
                    print "setting new agency_id:" + value
                if key in IDS:
                    value = value + AGENCY_ID
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

def load_agency(gtfs_path):
    print "loading agencies"
    #try:
    agencies = load_objects(gtfs_path + "agency.txt", "Agency")
    commit_objects(agencies)
    #except:
        #print "Error in loading agency.txt"
        #db.session.rollback()
        
def load_stops(gtfs_path):
    print "loading stops"
    try:
        stops = load_objects(gtfs_path + "stops.txt", "Stop")
        commit_objects(stops)
    except:
        print "Error in loading stops.txt"
        db.session.rollback()
        
def load_routes(gtfs_path):
    print "loading routes"
    try:
        routes = load_objects(gtfs_path + "routes.txt", "Route")
        commit_objects(routes)
    except:
        print "Error in loading routes.txt"
        db.session.rollback()
        
def load_trips(gtfs_path):
    print "loading trips"
    try:
        trips = load_objects(gtfs_path + "trips.txt", "Trip")
        commit_objects(trips)
    except:
        print "Error in loading trips.txt"
        db.session.rollback()
        
def load_stop_times(gtfs_path):
    print "loading stop_times"
    try:
        stop_times = load_objects(gtfs_path + "stop_times.txt", "StopTime", AGENCY_ID)
        commit_objects(stop_times)
        print "loaded stop_times"
    except:
        print "Error in loading stop_times.txt"
        db.session.rollback()
        
def load_calendar(gtfs_path):
    print "loading calendar"
    try:
        calendar = load_objects(gtfs_path + "calendar.txt", "Calendar")
        commit_objects(calendar)
    except:
        print "Error in loading calendar.txt"
        db.session.rollback()
        
def load_calendar_dates(gtfs_path):
    print "loading calendar dates"
    try:
        calendar_dates = load_objects(gtfs_path + "calendar_dates.txt", "CalendarDate")
        commit_objects(calendar_dates)
    except:
        print "Error in loading calendar_dates.txt"
        db.session.rollback()
        
def load_shapes(gtfs_path):
    print "loading shapes"
    try:
        shapes = load_objects(gtfs_path + "shapes.txt", "Shape", AGENCY_ID)
        commit_objects(shapes)
        print "loaded shapes"
    except:
        print "Error in loading shapes.txt"
        db.session.rollback()

def load_all(gtfs_path):
    # the order is important (necessary for relationships):
    # agencies must be loaded before routes (before everything else actually)
    load_agency(gtfs_path)
    # routes must be loaded before trips and before shapes
    load_routes(gtfs_path)
    # trips must be loaded before stop_times
    load_trips(gtfs_path)
    # stops must be loaded before stop_times 
    load_stops(gtfs_path)
    load_calendar(gtfs_path)
    load_calendar_dates(gtfs_path)
    thread.start_new_thread(load_shapes, (gtfs_path, ))
    thread.start_new_thread(load_stop_times, (gtfs_path, ))


