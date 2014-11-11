#!/usr/bin/env python

"""
Endpoint implementation for BDAS Cluster integration with AppDirect

Largely borrowed from https://github.com/AppDirect/Sample-Python-Application
"""

import logging
from xml.dom import minidom

import oauth2
from flask import request, Response, render_template, redirect

from . import app

from models.models import Cluster
from models.sl_config import SLConfig
from controller.clustermanager import create_cluster
from controller.handle_provisioning import get_cluster_status

from marshall import EventXml
from events import HandleEvent

from .forms import SLConfigForm


logger = logging.getLogger("endpoint")

event_url_template = 'https://www.appdirect.com/api/integration/v1/events/{}'

# AppDirect credentials
consumer_key = 'bdas-cluster-15877'
consumer_secret = 'PMBysgKaJtWZrOiq'

@app.route('/hello')
def hello():
    return 'Hello World'

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

@app.route('/cluster_create', methods=['POST', 'GET'])
def cluster_create():

    form = SLConfigForm()
    if form.validate_on_submit():
        logging.debug('sl_username={}, sl_api_key={}, sl_ssh_key={}, '
                      'sl_domain={},'
                      'sl_datacenter={}, num_workers={}, '
                      'sl_cpus={}, sl_memory={},'
                      'sl_disk_capacity={}, sl_network_speed={}'.format(
            form.sl_username.data, form.sl_api_key.data, form.sl_ssh_key.data,
            form.sl_domain.data,
            form.sl_datacenter.data, form.num_workers.data,
            form.sl_cpus.data, form.sl_memory.data,
            form.sl_disk_capacity.data, form.sl_network_speed.data
        ))

        sl_config = SLConfig(
            sl_username=form.sl_username.data,
            sl_api_key=form.sl_api_key.data,

            # TODO refactor hack with irina's ssh key
            sl_ssh_keys=['irina@ru.ibm.com', str(form.sl_ssh_key.data)],
            sl_private_key_path='~/.ssh/sftlyr.pem',

            sl_domain=form.sl_domain.data,
            sl_datacenter=form.sl_datacenter.data,
            num_workers=form.num_workers.data
        )
        owner_id = form.sl_username.data

        cluster_id = create_cluster(owner_id, sl_config)

        return redirect('/cluster_status?cluster_id={}'.format(cluster_id))
        # return redirect('/hello')

    return render_template('form.html', title='Home page', form=form)

@app.route('/cluster_status', methods=['POST', 'GET'])
def cluster_status():
    cluster_id = request.args.get('cluster_id')

    master_ip, log = get_cluster_status(cluster_id)

    # TODO prettify cluster log presentation
    return '<body>' \
           '<h3>master ip: {}</h3>' \
           '<p>You can login to master node using command: </p>' \
           '<pre>ssh -i &lt;path to your private key&gt; root@{}</pre>' \
           '<h3>Cluster provisioning log (please refresh manually)</h3>' \
           '<pre>{}</pre>' \
           '</body>'.format(master_ip, master_ip, log)
