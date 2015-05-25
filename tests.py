#!flask/bin/python
import os, zipfile, os, shutil
import unittest

from config import basedir
from app import app, db, models, gtfs_parser

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
        
    def gtfs_data_exists(self):
        assert os.path.isfile('UC_GTFS.zip')
        zfile = zipfile.ZipFile('UC_GTFS.zip')
        zfile.extractall('tmp/GTFS/')

    def load_agency(self):
        gtfs_parser.load_agency()
        agencies = models.Agency.query.all()
        assert len(agencies) > 0
        
    def load_routes(self):
        gtfs_parser.load_routes()
        routes = models.Route.query.all()
        assert len(routes) > 0

    def load_trips(self):
        gtfs_parser.load_trips()
        trips = models.Trip.query.all()
        assert len(trips) > 0
        
    def load_stops(self):
        gtfs_parser.load_stops()
        stops = models.Stop.query.all()
        assert len(stops) > 0
        
    def load_stop_times(self):
        gtfs_parser.load_stop_times()
        stop_times = models.StopTime.query.all()
        assert len(stop_times) > 0
        
    def load_calendar(self):
        gtfs_parser.load_calendar()
        calendar = models.Calendar.query.all()
        assert len(calendar) > 0
        
    def load_calendar_dates(self):
        gtfs_parser.load_calendar_dates()
        calendar_dates = models.CalendarDate.query.all()
        assert len(calendar_dates) > 0
        
    def load_shapes(self):
        gtfs_parser.load_shapes()
        shapes = models.Shape.query.all()
        assert len(shapes) > 0

    def remove_tmp(self):
        shutil.rmtree('tmp/GTFS')
        assert len([name for name in os.listdir('tmp/')]) == 0
        
    def test_load_gtfs(self):
        self.gtfs_data_exists()
        self.load_agency()
        self.load_routes()
        self.load_trips()
        self.load_stops()
        self.load_stop_times()
        self.load_calendar()
        self.load_calendar_dates()
        self.load_shapes()
        self.remove_tmp()

if __name__ == '__main__':
    unittest.main()