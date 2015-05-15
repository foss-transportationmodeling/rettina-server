import urllib2, json

UCONN_ROUTE_INFO_URL = 'http://www.uconnshuttle.com/Services/JSONPRelay.svc/GetRoutes'
ROUTE_STOPS_URL = 'http://www.uconnshuttle.com/Services/JSONPRelay.svc/GetMapStopEstimates'
VEHICLE_INFO_URL = 'http://www.uconnshuttle.com/Services/JSONPRelay.svc/GetMapVehiclePoints'
STOP_INFO_URL = 'http://www.uconnshuttle.com/Services/JSONPRelay.svc/GetStops'

def fetch_routes():
    uconn_routes = urllib2.urlopen(UCONN_ROUTE_INFO_URL)
    if (uconn_routes.getcode() == 200):    
        json_obj = json.load(uconn_routes)
        for route_info in json_obj:
            description = route_info["Description"]
            route_id = route_info["RouteID"]
            print description + " = %d" % route_id
        
def fetch_route_stops():
    route_stops = urllib2.urlopen(ROUTE_STOPS_URL)
    if (route_stops.getcode() == 200):
        json_obj = json.load(route_stops)
        for route_stop in json_obj:
            route_stop_id = route_stop["RouteStopID"]
            stop_order = route_stop["StopOrder"]
            description = route_stop["description"]
            for estimate in route_stop["estimates"]:
                on_route = estimate["OnRoute"]
                seconds_to_stop = estimate["SecondsToStop"]
                vehicle_id = estimate["VehicleID"]
            ending = "th"
            if (stop_order == 1):
                ending = "st"
            elif (stop_order == 2):
                ending = "nd"
            elif (stop_order == 3):
                ending = "rd"
            print description + (" = %d" % route_stop_id) + (" is %d" % stop_order) + ending
            
def fetch_vehicle_info():
    vehicle_info = urllib2.urlopen(VEHICLE_INFO_URL)
    if (vehicle_info.getcode() == 200):
        json_obj = json.load(vehicle_info)
        for vehicle in json_obj:
            ground_speed = vehicle["GroundSpeed"]
            heading = vehicle["Heading"]
            is_delayed = vehicle["IsDelayed"]
            is_on_route = vehicle["IsOnRoute"]
            latitude = vehicle["latitude"]
            longitude = vehicle["Longitude"]
            name = vehicle["Name"]
            route_id = vehicle["RouteID"]
            seconds = vehicle["Seconds"]
            timestamp = vehicle["Timestamp"]
            vehicle_id = vehicle["VehicleID"]
            print ("Vehicle %d" + vehicle_id) + (" is going at a speed of %f" + ground_speed)

def fetch_stop_info():
    stop_info = urllib2.urlopen(STOP_INFO_URL)
    if (stop_info.getcode() == 200):
        json_obj = json.load(stop_info)
        for stop in json_obj:
            description = stop["Description"]
            latitude = stop["Latitude"]
            longitude = stop["Longitude"]
            for map_point in stop["MapPoints"]:
                heading = map_point["Heading"]
                latitude = map_point["Latitude"]
                longitude = map_point["Longitude"]
            print description + " is at " + ("%f, %f" % (latitude, longitude))
           
import math          
def km_distance(lat1, lon1, lat2, lon2):
    def to_radians(degrees):
        return degrees * math.pi / 180.0

    R = 6371
    phi1 = to_radians(lat1)
    phi2 = to_radians(lat2)
    delta_phi = to_radians(lat2 - lat1)
    delta_lambda = to_radians(lon2 - lon1)

    a = math.pow(math.sin(delta_phi / 2.0), 2) + math.cos(phi1) * math.cos(phi2) * math.pow(math.sin(delta_lambda / 2.0), 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    
    return d
            
# shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence,shape_dist_traveled            

class ShapeItem:
    shape_id = None # will correspond to route_id
    lat = None
    lon = None
    order = None
    dist_traveled = None
    def __init__(self, shape_id, lat, lon):
        self.shape_id = shape_id
        self.lat = lat
        self.lon = lon
    def to_str(self):
        str1 = str(self.shape_id) + "," + str(self.lat) + "," + str(self.lon) + ","
        str2 = str(self.order) + "," + str(self.dist_traveled)
        return str1 + str2

def load_shapes():
    stop_info = urllib2.urlopen(STOP_INFO_URL)
    file = open('/Users/trevphil/Desktop/UC_GTFS/shapes.txt', 'w')
    if (stop_info.getcode() == 200):
        json_obj = json.load(stop_info)
        shapes = []
        for stop in json_obj:
            shape_id = stop["RouteID"]
            for map_point in stop["MapPoints"]:
                latitude = map_point["Latitude"]
                longitude = map_point["Longitude"]
                shape = ShapeItem(shape_id, latitude, longitude)
                shapes.append(shape)
        last_shape_id = -1
        order = 1
        base_lat = 999
        base_lon = 999
        for shape in shapes:
            if not shape.shape_id == last_shape_id:
                order = 1
                last_shape_id = shape.shape_id
                base_lat = shape.lat
                base_lon = shape.lon
                shape.dist_traveled = 0.0
            else:
                shape.dist_traveled = km_distance(base_lat, base_lon, shape.lat, shape.lon)
            shape.order = order
            order = order + 1
            file.write(shape.to_str() + "\n")
            
load_shapes()
