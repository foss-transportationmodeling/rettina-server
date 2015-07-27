import threading
import gtfs_parser
from app import db

class MyThread (threading.Thread):
    def __init__(self, name, file_name, object_name, thread_lock):
        threading.Thread.__init__(self)
        self.name = name
        self.file_name = file_name
        self.object_name = object_name
        self.thread_lock = thread_lock
    def run(self):
        print "Starting " + self.name
        # Get lock to synchronize threads
        self.thread_lock.acquire()
        # Do the dirty work
        try:
            objects = gtfs_parser.load_objects(gtfs_parser.GTFS_PATH + self.file_name, self.object_name)
            gtfs_parser.commit_objects(objects)
        except:
            print "Error in loading " + self.file_name
            db.session.rollback()
        # Free lock to release next thread
        self.thread_lock.release()