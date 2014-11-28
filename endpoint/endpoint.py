#!/usr/bin/env python

"""
Endpoint implementation for BDAS Cluster integration with AppDirect

Largely borrowed from https://github.com/AppDirect/Sample-Python-Application
"""

import logging
from xml.dom import minidom
import traceback
import sys

import oauth2
from flask import request, Response, render_template, redirect, flash, session
import SoftLayer

from . import app
from models.models import Cluster
from models.sl_config import SLConfig
from controller.clustermanager import create_cluster, get_master_ip_and_password, \
    destroy_cluster, suspend_cluster, resume_cluster
from controller.handle_provisioning import get_cluster_status
from .marshall import EventXml
from .events import HandleEvent
from .forms import SLConfigForm


logger = logging.getLogger("endpoint")

event_url_template = 'https://www.appdirect.com/api/integration/v1/events/{}'

# AppDirect credentials
consumer_key = 'bdas-cluster-15877'
consumer_secret = 'PMBysgKaJtWZrOiq'


def getClient(username, apikey):
    # Note: this does not raise a SL exception, even if the api key is wrong
    return SoftLayer.Client(username=username, api_key=apikey,
                            endpoint_url=SoftLayer.API_PUBLIC_ENDPOINT)


# def verifyCredentials():
# '''Make a trivial api call to SL to verify the username and api key.'''
#     try:
#         user = self.client['Account'].getCurrentUser(mask='email')
#         return 200, 'SoftLayer credentials ok'
#     except SoftLayer.exceptions.SoftLayerAPIError as e:
#         if isAuthProb(e.faultString):  return 403, str(e.faultCode) + ': ' + e.faultString
#         else:  return 502, str(e.faultCode) + ': ' + e.faultString

@app.route("/")
def index():
    return render_template('uilogin.html')


@app.route('/uilogin', methods=['GET', 'POST'])
def login():
    try:
        if "username" in request.form:
            userName = request.form['username']
        else:
            userName = None
        if "apikey" in request.form:
            apiKey = request.form['apikey']
        else:
            apiKey = None

        if (request.method == 'POST') and userName != None and apiKey != None:

            # User id and API key have been submitted so now we need to authenticate the user
            # and check for any missing ACLs that might later halt the process.
            #

            try:

                client = getClient(userName, apiKey)
                user = client['Account'].getCurrentUser(mask='email')
                useremail = user["email"]

            except SoftLayer.exceptions.SoftLayerAPIError as e:
                flash("Failed Authentication")
                return redirect("/")

            except Exception as e:
                msg = ["Internal error occurred:" + e.args[
                    0] + ". Please contact support."]
                flash(msg)
                traceback.print_exc()
                return redirect("/")

            # If the user was authenticated then we can store the user's info in the HTTP session
            # object and then begin the workflow for gathering config info
            #
            session['username'] = userName
            session['useremail'] = useremail
            session['apikey'] = apiKey

            return _dashboard()

        elif request.method == "POST":
            # The user did not specify all the required login information.
            #
            if ( not userName ):
                msg = ['Please specify your SoftLayer user id.']
            elif (not apiKey):
                msg = ['Please specify your SoftLayer API Key.']
            else:
                msg = [
                    'Please specify your email address when acting as an agent for the user.']
            flash(msg)
            return redirect("/")

        else:
            return redirect("/")

    except Exception as e:
        traceback.print_exc()
        msg = ["Internal error occurred:" + e.args[
            0] + ". Please contact support."]
        flash(msg)

    return redirect("/uilogin")


@app.route('/uilogout')
def logout():
    session.pop('username', None)
    session.pop('apikey', None)
    session.pop("useremail")
    return redirect('/')


@app.route('/login', methods=['POST', 'GET'])
def _login():
    logging.debug('request.args={}'.format(request.args))

    openid = request.args.get('openid')

    # remove url beginning from openid, leave uuid
    openid = openid.split('/')[-1]

    account_id = request.args.get('accountIdentifier')
    cluster = Cluster.by_openid(openid)
    return "openid = {}, cluster = {}".format(openid, cluster)


@app.route('/event', methods=['POST', 'GET'])
def _event():
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


@app.route('/dashboard', methods=['POST', 'GET'])
def _dashboard():
    if not logged_in():
        return redirect('/')

    return render_template('dashboard.html', title='Dashboard',
                           username=session["username"],
                           clusters=Cluster.by_owner_id(session["username"]))


@app.route('/about', methods=['POST', 'GET'])
def _about():
    if not logged_in():
        return redirect('/')

    return render_template('about.html', title='About',
                           username=session["username"])


@app.route('/help', methods=['POST', 'GET'])
def _help():
    if not logged_in():
        return redirect('/')

    return render_template('help.html', title='Help',
                           username=session["username"])


@app.route('/create_cluster', methods=['POST', 'GET'])
def _create_cluster():
    if not logged_in():
        return redirect('/')

    form = SLConfigForm()
    if form.validate_on_submit():
        logging.debug('cluster_name={},sl_ssh_key={}, '
                      'sl_domain={},'
                      'sl_datacenter={}, num_workers={}, '
                      'sl_cpus={}, sl_memory={},'
                      'sl_disk_capacity={}, sl_network_speed={}'.format(
            form.cluster_name.data, form.sl_ssh_key.data,
            form.sl_domain.data,
            form.sl_datacenter.data, form.num_workers.data,
            form.sl_cpus.data, form.sl_memory.data,
            form.sl_disk_capacity.data, form.sl_network_speed.data
        ))

        # TODO refactor hack with irina's ssh key
        ssh_keys = ['irina@ru.ibm.com']
        private_key_path = '~/.ssh/sftlyr.pem'
        if len(str(form.sl_ssh_key.data)) > 0:
            ssh_keys.append(form.sl_ssh_key.data)

        sl_config = SLConfig(
            sl_username=session["username"],
            sl_api_key=session["apikey"],

            cpus=form.sl_cpus.data,
            memory=form.sl_memory.data,
            disk_capacity=form.sl_disk_capacity.data,
            network_speed=form.sl_network_speed.data,

            sl_ssh_keys=ssh_keys,
            sl_private_key_path=private_key_path,

            sl_domain=form.sl_domain.data,
            sl_datacenter=form.sl_datacenter.data,
            num_workers=form.num_workers.data
        )
        owner_id = session["username"]

        cluster_id = create_cluster(owner_id, sl_config,
                                    form.cluster_name.data)

        return redirect('/cluster_status?cluster_id={}'.format(cluster_id))

        # else:
        # flash("hi")

    return render_template('form.html', title='Create Cluster', form=form,
                           username=session["username"])


@app.route('/view', methods=['POST', 'GET'])
def _view():
    if not logged_in():
        return redirect('/')

    cluster_id = request.args.get('cluster_id')

    cluster = Cluster.by_uuid(cluster_id)

    return render_template('view.html', title='View Cluster',
                           cluster_id=cluster_id,
                           cluster_state=cluster.cluster_state,
                           username=session["username"],
                           cluster_name=cluster.cluster_name,
                           num_workers=cluster.num_workers,
                           cpus=cluster.cpus,
                           memory=cluster.memory,
                           disk_capacity=cluster.disk_capacity,
                           network_speed=cluster.network_speed,
                           sl_ssh_key=cluster.sl_ssh_key,
                           sl_domain=cluster.sl_domain,
                           sl_datacenter=cluster.sl_datacenter,
                           master_ip=cluster.master_ip,
                           master_password=cluster.master_password
    )


@app.route('/delete', methods=['POST', 'GET'])
def _delete():
    if not logged_in():
        return redirect('/')

    cluster_id = request.args.get('cluster_id')

    destroy_cluster(cluster_id)

    return _dashboard()


@app.route('/suspend', methods=['POST', 'GET'])
def _suspend():
    if not logged_in():
        return redirect('/')

    cluster_id = request.args.get('cluster_id')

    suspend_cluster(cluster_id)

    return _dashboard()


@app.route('/resume', methods=['POST', 'GET'])
def _resume():
    if not logged_in():
        return redirect('/')

    cluster_id = request.args.get('cluster_id')

    resume_cluster(cluster_id)

    return _dashboard()


@app.route('/master_ip', methods=['POST', 'GET'])
def _master_ip():
    cluster_id = request.args.get('cluster_id')

    master_ip, master_password = get_master_ip_and_password(cluster_id)

    return master_ip


@app.route('/master_password', methods=['POST', 'GET'])
def _master_password():
    cluster_id = request.args.get('cluster_id')

    master_ip, master_password = get_master_ip_and_password(cluster_id)

    return master_password


@app.route('/cluster_status', methods=['POST', 'GET'])
def _cluster_status():
    cluster_id = request.args.get('cluster_id')

    master_ip, stdout, stderr = get_cluster_status(cluster_id)

    master_ip, master_password = get_master_ip_and_password(cluster_id)

    # TODO prettify cluster log presentation
    return render_template('cluster_status.html',
                           cluster_id=cluster_id,
                           master_ip=master_ip,
                           master_password=master_password,
                           stdout=stdout,
                           stderr=stderr,
                           username=session["username"])


@app.route('/cluster_stdout', methods=['POST', 'GET'])
def _cluster_stdout():
    cluster_id = request.args.get('cluster_id')

    master_ip, stdout, stderr = get_cluster_status(cluster_id)
    return stdout


@app.route('/cluster_stderr', methods=['POST', 'GET'])
def _cluster_stderr():
    cluster_id = request.args.get('cluster_id')

    master_ip, stdout, stderr = get_cluster_status(cluster_id)
    return stderr



def logged_in():
    if 'username' in session and 'apikey' in session:
        return True
    return False