from app import db

# add fields such as required, default value, positive integer

class Agency(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    agency_id = db.Column(db.String(64), unique = True)
    agency_name = db.Column(db.String(128))
    agency_url = db.Column(db.String(256))
    agency_timezone = db.Column(db.String(64))
    agency_phone = db.Column(db.String(32))
    agency_lang = db.Column(db.String(2))
    agency_fare_url = db.Column(db.String(256))
    def serialize(self):
        return {
            'agency_id' : self.agency_id,
            'agency_name' : self.agency_name,
            'agency_url' : self.agency_url,
            'agency_timezone' : self.agency_timezone,
            'agency_phone' : self.agency_phone,
            'agency_lang' : self.agency_lang,
            'agency_phone' : self.agency_phone,
            'agency_fare_url' : self.agency_fare_url
        }
    
class Stop(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    stop_id = db.Column(db.String(32), unique = True)
    stop_code = db.Column(db.String(16))
    stop_name = db.Column(db.String(128))
    stop_desc = db.Column(db.Text)
    stop_lat = db.Column(db.Float)
    stop_lon = db.Column(db.Float)
    zone_id = db.Column(db.String(32))
    stop_url = db.Column(db.String(256))
    location_type = db.Column(db.Integer)
    parent_station = db.Column(db.String(32))
    stop_timezone = db.Column(db.String(2))
    wheelchair_boarding = db.Column(db.Integer)
    def serialize(self):
        return {
            'stop_id' : self.stop_id,
            'stop_code' : self.stop_code,
            'stop_name' : self.stop_name,
            'stop_desc' : self.stop_desc,
            'stop_lat' : self.stop_lat,
            'stop_lon' : self.stop_lon,
            'zone_id' : self.zone_id,
            'stop_url' : self.stop_url,
            'location_type' : self.location_type,
            'parent_station' : self.parent_station,
            'stop_timezone' : self.stop_timezone,
            'wheelchair_boarding' : self.wheelchair_boarding
        }
    
class Route(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    route_id = db.Column(db.String(32), unique = True)
    route_short_name = db.Column(db.String(256))
    route_long_name = db.Column(db.String(512))
    route_desc = db.Column(db.Text)
    route_type = db.Column(db.Integer)
    route_url = db.Column(db.String(256))
    route_color = db.Column(db.String(6), default = "FFFFFF")
    route_text_color = db.Column(db.String(6), default = "000000")
    agency_id = db.Column(db.Integer, db.ForeignKey('agency.id'))
    agency = db.relationship('Agency', backref = db.backref('routes', lazy = 'dynamic'))
    def serialize(self):
        return {
            'route_id' : self.route_id,
            'agency_id' : self.agency.agency_id,
            'agency_name' : self.agency.agency_name,
            'trip_ids' : [trip.trip_id for trip in self.trips],
            'route_short_name' : self.route_short_name,
            'route_long_name' : self.route_long_name,
            'route_desc' : self.route_desc,
            'route_type' : self.route_type,
            'route_url' : self.route_url,
            'route_color' : self.route_color,
            'route_text_color' : self.route_text_color
        }
    
stops = db.Table('stops',
    db.Column('stop_id', db.Integer, db.ForeignKey('stop.id')),
    db.Column('trip_id', db.Integer, db.ForeignKey('trip.id'))
)
    
class Trip(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    service_id = db.Column(db.String(32))
    trip_id = db.Column(db.String(32), unique = True)
    trip_headsign = db.Column(db.String(32))
    trip_short_name = db.Column(db.String(64))
    direction_id = db.Column(db.Integer)
    block_id = db.Column(db.Integer)
    shape_id = db.Column(db.Integer)
    wheelchair_accessible = db.Column(db.Integer)
    bikes_allowed = db.Column(db.Integer)
    stops = db.relationship('Stop', secondary = stops, 
        backref = db.backref('trips', lazy = 'dynamic'))
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    route = db.relationship('Route', backref = db.backref('trips', lazy = 'dynamic'))
    def serialize(self):
        return {
            'route_id' : self.route.route_id,
            'service_id' : self.service_id,
            'trip_id' : self.trip_id,
            'trip_headsign' : self.trip_headsign,
            'trip_short_name' : self.trip_short_name,
            'direction_id' : self.direction_id,
            'block_id' : self.block_id,
            'shape_id' : self.shape_id,
            'wheelchair_accessible' : self.wheelchair_accessible,
            'bikes_allowed' : self.bikes_allowed
        }
    
class StopTime(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))
    trip = db.relationship('Trip', backref = db.backref('stop_times', lazy = 'dynamic'))
    arrival_time = db.Column(db.String(16))
    departure_time = db.Column(db.String(16))
    stop_id = db.Column(db.String(32))
    stop_sequence = db.Column(db.Integer)
    stop_headsign = db.Column(db.String(64))
    pickup_type = db.Column(db.Integer)
    drop_off_type = db.Column(db.Integer)
    shape_dist_traveled = db.Column(db.String(32))
    timepoint = db.Column(db.Integer)
    stop_lat = db.Column(db.Float)
    stop_lon = db.Column(db.Float)
    def serialize(self):
        return {
            'arrival_time' : self.arrival_time,
            'departure_time' : self.departure_time,
            'stop_id' : self.stop_id,
            'stop_sequence' : self.stop_sequence,
            'stop_headsign' : self.stop_headsign,
            'pickup_type' : self.pickup_type,
            'drop_off_type' : self.drop_off_type,
            'shape_dist_traveled' : self.shape_dist_traveled,
            'timepoint' : self.timepoint,
            'stop_lat' : self.stop_lat,
            'stop_lon' : self.stop_lon,
            'trip_id' : self.trip.trip_id
        }
    
class Calendar(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    service_id = db.Column(db.String(32))
    monday = db.Column(db.Integer)
    tuesday = db.Column(db.Integer)
    wednesday = db.Column(db.Integer)
    thursday = db.Column(db.Integer)
    friday = db.Column(db.Integer)
    saturday = db.Column(db.Integer)
    sunday = db.Column(db.Integer)
    start_date = db.Column(db.String(16))
    end_date = db.Column(db.String(16))
    def serialize(self):
        return {
            'service_id' : self.service_id,
            'monday' : self.monday,
            'tuesday' : self.tuesday,
            'wednesday' : self.wednesday,
            'thursday' : self.thursday,
            'friday' : self.friday,
            'saturday' : self.saturday,
            'sunday' : self.sunday,
            'start_date' : self.start_date,
            'end_date' : self.end_date
        }
    
class CalendarDate(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    service_id = db.Column(db.String(32))
    date = db.Column(db.String(16))
    exception_type = db.Column(db.Integer)
    def serialize(self):
        return {
            'service_id' : self.service_id,
            'date' : self.date,
            'exception_type' : self.exception_type
        }

class Shape(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    shape_pt_lat = db.Column(db.Float)
    shape_pt_lon = db.Column(db.Float)
    shape_pt_sequence = db.Column(db.Integer)
    shape_dist_traveled = db.Column(db.Float)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))
    route = db.relationship('Route', backref = db.backref('shapes', lazy = 'dynamic'))
    def serialize(self):
        return {
            'shape_id' : self.route.route_id,
            'shape_pt_lat' : self.shape_pt_lat,
            'shape_pt_lon' : self.shape_pt_lon,
            'shape_pt_sequence' : self.shape_pt_sequence,
            'shape_dist_traveled' : self.shape_dist_traveled
        }
    
    
    
    
