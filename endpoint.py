#!/usr/bin/env python

"""
Endpoint implementation for BDAS Cluster integration with AppDirect

Largely borrowed from https://github.com/AppDirect/Sample-Python-Application
"""

import logging

from xml.dom import minidom

# for getting xml info from event url, todo: replace by oauth2 request
import requests
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

    # fetch event info from REST API event_url_template
    # see docs at http://info.appdirect.com/developers/docs/api_integration/subscription_management/subscription_order_event
    event_url = event_url_template.format(token)
    response = requests.get(event_url)

    # parse xml response
    if response.status_code == 200:
        xml_document = minidom.parseString(response.content)
        event_xml = EventXml(xml_document)

        logging.debug(event_xml.prettyPrint)

        # handle event: create order
        xml_response = HandleEvent(event_xml)
    else:
        xml_response = xml_order_error.format('UNKNOWN_ERROR', response.status_code)

    logging.debug(xml_response)
    return Response(xml_response, mimetype='text/xml')

if __name__ == "__main__":
    app.debug = True
    app.run('0.0.0.0')

