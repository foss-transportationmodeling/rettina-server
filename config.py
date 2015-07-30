import os
import MySQLdb

basedir = os.path.abspath(os.path.dirname(__file__))

# this was the initial database URI, for using SQLite
#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

# 'app' is the name of the MySQL database
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:1234@localhost/app'

# migration versions are saved under db_repository
# If you are wiping the database and want to start at version 1 again,
# it is fine to completely delete this directory. It will be created again.
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
