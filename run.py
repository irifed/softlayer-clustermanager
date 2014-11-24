#!/usr/bin/env python3
import logging

from endpoint import app
from models.models import db

logging.basicConfig(
    format='%(asctime)s: %(levelname)s: %(filename)s: %(funcName)s(): %(message)s',
    level=logging.ERROR)

logging.getLogger('SoftLayer').setLevel(logging.WARNING)

logger = logging.getLogger('endpoint')
logger.setLevel(level=logging.DEBUG)



def connect_db():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/clusters/test.db'
    db.init_app(app)
    with app.app_context():
        # db.drop_all() # DEBUG uncomment to reset tables for debugging
        db.create_all()


if __name__ == "__main__":
    connect_db()

    app.debug = True
    app.run('0.0.0.0')

