#!/usr/bin/env python

"""
Endpoint implementation for BDAS Cluster integration with AppDirect

Largely borrowed from https://github.com/AppDirect/Sample-Python-Application
"""

import logging

from xml.dom import minidom

import oauth2

from flask import Flask, request, Response

from models import db
from marshall import EventXml
from events import HandleEvent, xml_order_error

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db.init_app(app)
with app.app_context():
    # db.drop_all() # DEBUG uncomment to reset tables for debugging
    db.create_all()

event_url_template = 'https://www.appdirect.com/api/integration/v1/events/{}'

consumer_key = 'bdas-cluster-15877'
consumer_secret = 'PMBysgKaJtWZrOiq'

#logging.basicConfig(filename='example.log', level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/login', methods=['POST', 'GET'])
def login():
    logging.debug(request.args)

    name = request.args.get('name')
    return "LOGIN: name={}".format(name)

@app.route('/order', methods=['POST', 'GET'])
def order():
    logging.debug(request.args)

    # TODO guard by try..catch
    token = request.args.get('token')

    # fetch event info from REST API by `token`
    # see docs at http://info.appdirect.com/developers/docs/api_integration/subscription_management/subscription_order_event
    event_url = event_url_template.format(token)
    consumer = oauth2.Consumer(consumer_key, consumer_secret)
    client = oauth2.Client(consumer)
    response, content = client.request(event_url)

    # parse xml response
    if int(response['status']) == 200:
        xml_document = minidom.parseString(content)
        event_xml = EventXml(xml_document)

        logging.debug(event_xml.prettyPrint)

        # handle event: create order
        xml_response = HandleEvent(event_xml)
    else:
        xml_response = xml_order_error.format(response.status_code, response.content)

    logging.debug(xml_response)
    return Response(xml_response, mimetype='text/xml')

if __name__ == "__main__":
    app.debug = True
    app.run('0.0.0.0')

