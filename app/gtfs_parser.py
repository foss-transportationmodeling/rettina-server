from app import db, models

GTFS_PATH = "tmp/GTFS/UC_GTFS/"

def load_objects(file, name):
    objects = []
    f = open(file, 'r')
    clean_first_line = f.readline().strip().replace(' ', '')
    keys = clean_first_line.split(',')
    for line in f:
        obj = object_for_name(name)
        values = line.strip().split(',')
        for i, key in enumerate(keys):
            if hasattr(obj, key):
                try:
                    setattr(obj, key, values[i])
                except IndexError:
                    print "A value is missing from " + file
        objects.append(obj)
    return objects

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

def commit_objects(objects):
    for obj in objects:
        db.session.add(obj)
    db.session.commit()

def add_coordinates(stop_times):
    for stop_time in stop_times:
        stop = models.Stop.query.filter(models.Stop.stop_id == stop_time.stop_id).first()
        if not stop is None:
            setattr(stop_time, 'stop_lat', stop.stop_lat)
            setattr(stop_time, 'stop_lon', stop.stop_lon)

def load_agency():
    print "loading agencies"
    try:
        agencies = load_objects(GTFS_PATH + "agency.txt", "Agency")
        commit_objects(agencies)
    except:
        print "Error in loading agency.txt"
        db.session.rollback()
def load_stops():
    try:
        stops = load_objects(GTFS_PATH + "stops.txt", "Stop")
        commit_objects(stops)
    except:
        print "Error in loading stops.txt"
        db.session.rollback()
def load_routes():
    try:
        routes = load_objects(GTFS_PATH + "routes.txt", "Route")
        commit_objects(routes)
    except:
        print "Error in loading routes.txt"
        db.session.rollback()
def load_trips():
    try:
        trips = load_objects(GTFS_PATH + "trips.txt", "Trip")
        commit_objects(trips)
    except:
        print "Error in loading trips.txt"
        db.session.rollback()
def load_stop_times():
    try:
        stop_times = load_objects(GTFS_PATH + "stop_times.txt", "StopTime")
        add_coordinates(stop_times)
        commit_objects(stop_times)
    except:
        print "Error in loading stop_times.txt"
        db.session.rollback()
def load_calendar():
    try:
        calendar = load_objects(GTFS_PATH + "calendar.txt", "Calendar")
        commit_objects(calendar)
    except:
        print "Error in loading calendar.txt"
        db.session.rollback()
def load_calendar_dates():
    try:
        calendar_dates = load_objects(GTFS_PATH + "calendar_dates.txt", "CalendarDate")
        commit_objects(calendar_dates)
    except:
        print "Error in loading calendar_dates.txt"
        db.session.rollback()
def load_shapes():
    try:
        shapes = load_objects(GTFS_PATH + "shapes.txt", "Shape")
        commit_objects(shapes)
    except:
        print "Error in loading shapes.txt"
        db.session.rollback()

def load_all():
    load_agency()
    load_stops()
    load_routes()
    load_trips()
    load_stop_times()
    load_calendar()
    load_calendar_dates()
    load_shapes()


