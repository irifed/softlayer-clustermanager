#!/usr/bin/env python

"""
Endpoint implementation for BDAS Cluster integration with AppDirect

Largely borrowed from https://github.com/AppDirect/Sample-Python-Application
"""

import logging

from xml.dom import minidom

import oauth2

from flask import Flask, request, Response

from models import db, Cluster
from marshall import EventXml
from events import HandleEvent


event_url_template = 'https://www.appdirect.com/api/integration/v1/events/{}'

consumer_key = 'bdas-cluster-15877'
consumer_secret = 'PMBysgKaJtWZrOiq'

#logging.basicConfig(filename='example.log', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(filename)s: %(funcName)s(): %(message)s')
logger = logging.getLogger("endpoint")

app = Flask(__name__)

def connect_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    db.init_app(app)
    with app.app_context():
        # db.drop_all() # DEBUG uncomment to reset tables for debugging
        db.create_all()
    return app

@app.route('/login', methods=['POST', 'GET'])
def login():
    logging.debug('request.args={}'.format(request.args))

    openid = request.args.get('openid')

    # remove url beginning from openid, leave uuid
    openid = openid.split('/')[-1]

    account_id = request.args.get('accountIdentifier')
    cluster = Cluster.by_openid(openid)
    return "openid = {}, cluster = {}".format(openid, cluster)

@app.route('/event', methods=['POST', 'GET'])
def event():
    logging.debug('request.args = {}'.format(request.args))

    # TODO guard by try..catch
    token = request.args.get('token')
    logging.debug('token = {}'.format(token))

    # set up OAuth client
    consumer = oauth2.Consumer(consumer_key, consumer_secret)
    client = oauth2.Client(consumer)

    # fetch event info from REST API by `token`
    # see docs at http://info.appdirect.com/developers/docs/api_integration/subscription_management/subscription_order_event
    event_url = event_url_template.format(token)
    response, content = client.request(event_url)

    # parse xml response
    if int(response['status']) == 200:
        xml_document = minidom.parseString(content)
        event_xml = EventXml(xml_document)

        logging.debug(event_xml.prettyPrint)

        # handle event: create order
        xml_response = HandleEvent(event_xml)
    else:
        xml_response = content

    logging.debug('xml_response=\n{}\n'.format(xml_response))

    return Response(xml_response, mimetype='text/xml')

if __name__ == "__main__":
    app = connect_db(app)

    app.debug = True
    app.run('0.0.0.0')

