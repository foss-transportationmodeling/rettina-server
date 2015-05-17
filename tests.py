#!flask/bin/python
import os
import unittest

from config import basedir
from app import app, db

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        
    def test_gtfs_data_exists(self):
        assert os.path.isfile('UC_GTFS.zip')

    def test_load_agency(self):
        load_agency()
        agencies = models.Agency.query.all()
        assert len(agencies) > 0
        
    def test_load_routes(self):
        load_routes()
        routes = models.Route.query.all()
        assert len(routes) > 0

    def test_load_trips(self):
        load_trips()
        trips = models.Trip.query.all()
        assert len(trips) > 0
        
    def test_load_stops(self):
        load_stops()
        stops = models.Stop.query.all()
        assert len(stops) > 0
        
    def test_load_stop_times(self):
        load_stop_times()
        stop_times = models.StopTime.query.all()
        assert len(stop_times) > 0
        
    def test_load_calendar(self):
        load_calendar()
        calendar = models.Calendar.query.all()
        assert len(calendar) > 0
        
    def test_load_calendar_dates(self):
        load_calendar_dates()
        calendar_dates = models.CalendarDate.query.all()
        assert len(calendar_dates) > 0
        
    def test_load_shapes(self):
        load_shapes()
        shapes = models.Shape.query.all()
        assert len(shapes) > 0

if __name__ == '__main__':
    unittest.main()