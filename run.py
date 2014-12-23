#!/usr/bin/env python3
import logging

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from views import app
from models.models import db

format = '%(asctime)s: %(levelname)s: %(filename)s: %(funcName)s(): %(message)s'
logging.basicConfig(
    format=format,
    level=logging.ERROR)

logging.getLogger('SoftLayer').setLevel(logging.WARNING)

logger = logging.getLogger('clustermanager')
logger.setLevel(level=logging.DEBUG)

logfh = logging.FileHandler('/var/logs/clustermanager.log')
logfh.setFormatter(logging.Formatter(format))
logger.addHandler(logfh)

def connect_db():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/clusters/test.db'
    db.init_app(app)
    with app.app_context():
        # db.drop_all() # DEBUG uncomment to reset tables for debugging
        db.create_all()


if __name__ == "__main__":
    connect_db()

    app.debug = True

    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)
    IOLoop.instance().start()
