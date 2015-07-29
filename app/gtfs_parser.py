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
                
def load_objects(file, name, agency_name = ""):
    try:
        with open(file, 'r') as f:
            print "Loading " + name + ":\t" + agency_name
            batch_num = 1
            objects_added = 0
            clean_first_line = f.readline().strip().replace(' ', '')
            keys = clean_first_line.split(',')
            for line in f:
                obj = object_for_name(name)
                values = line.strip().split(',')
                if len(values) == 0:
                    continue
                for i, key in enumerate(keys):
                    value = values[i].strip()
                    if key in IDS:
                        value = value + " " + agency_name
                    # handle special cases for setting relationships
                    if name == "Agency" and key == "agency_name":
                        agency_name = value
                    elif name == "StopTime" and key == "trip_id":
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
                    elif hasattr(obj, key):
                        setattr(obj, key, value)
                db.session.add(obj)
                objects_added = objects_added + 1
                if objects_added >= 1500:
                    db.session.commit()
                    objects_added = 0
                    print "Loaded batch " + str(batch_num)
                    batch_num = batch_num + 1
            f.close()
            db.session.commit()
            if batch_num == 1:  
                print "Loaded " + name + ":\t" + agency_name
            else:
                print "Loaded " + name + ":\t" + agency_name + "\t(finished: batch " + str(batch_num) + ")"
    except IndexError, e:
        print "A value is missing from " + file + ":\t" + str(e)
        db.session.rollback()
    except e:
        print "Error in loading " + file + ":\t" + str(e)
        db.session.rollback()
    return agency_name
    
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

def load_all(gtfs_path):
    # the order is important (necessary for relationships):
    # agencies must be loaded before routes (before everything else actually)
    agency_name = load_objects(gtfs_path + "agency.txt", "Agency")
    # routes must be loaded before trips and before shapes
    load_objects(gtfs_path + "routes.txt", "Route", agency_name)
    # trips must be loaded before stop_times
    load_objects(gtfs_path + "trips.txt", "Trip", agency_name)
    # stops must be loaded before stop_times 
    load_objects(gtfs_path + "stops.txt", "Stop", agency_name)
    load_objects(gtfs_path + "calendar.txt", "Calendar", agency_name)
    load_objects(gtfs_path + "calendar_dates.txt", "CalendarDate", agency_name)
    load_objects(gtfs_path + "shapes.txt", "Shape", agency_name)
    load_objects(gtfs_path + "stop_times.txt", "StopTime", agency_name)
    #thread.start_new_thread(load_shapes, (gtfs_path, agency.agency_name, ))
    #thread.start_new_thread(load_stop_times, (gtfs_path, agency.agency_name, ))


