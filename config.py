import os

basedir = os.path.abspath(os.path.dirname(__file__))

#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:1234@localhost/app'

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')