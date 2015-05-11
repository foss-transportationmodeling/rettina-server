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
            
fetch_route_stops()
