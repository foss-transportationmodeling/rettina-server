#!flask/bin/python

from app import app

# set debug to True to enable more output and error messages
# Be warned though: if loading large datasets, debug = True
# may slow the application to such a degree that the application is killed
if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = False)

