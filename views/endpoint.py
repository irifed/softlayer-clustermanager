#!/usr/bin/env python

"""
Endpoint implementation for BDAS Cluster integration with AppDirect

Largely borrowed from https://github.com/AppDirect/Sample-Python-Application
"""

import logging
import traceback
import pickle

from flask import request, render_template, redirect, flash, session
import SoftLayer

from . import app
from models.models import Cluster
from models.sl_config import SLConfig
from models.components import Components
from controller.clustermanager import create_cluster, \
    get_master_ip_and_password, destroy_cluster
from controller.handle_provisioning import get_cluster_status
from .forms import SLConfigForm


logger = logging.getLogger('clustermanager')


def getClient(username, apikey):
    # Note: this does not raise a SL exception, even if the api key is wrong
    return SoftLayer.Client(username=username, api_key=apikey,
                            endpoint_url=SoftLayer.API_PUBLIC_ENDPOINT)


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

        if (
                    request.method == 'POST') and userName is not None and apiKey is not None:

            # User id and API key have been submitted so now we need to authenticate the user
            # and check for any missing ACLs that might later halt the process.
            #

            try:

                client = getClient(userName, apiKey)
                user = client['Account'].getCurrentUser(mask='email')
                useremail = user["email"]

            except SoftLayer.exceptions.SoftLayerAPIError:
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
            if not userName:
                msg = ['Please specify your SoftLayer user id.']
            elif not apiKey:
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
                      'sl_domain={}, '
                      'sl_datacenter={}, num_workers={}, '
                      'sl_cpus={}, sl_memory={}, '
                      'sl_disk_capacity={}, sl_network_speed={}, '
                      'install_spark={}, install_mpi={}, '
                      'install_mapred={}, install_mesos={}, '
                      'install_hive={}, install_cassandra={}, '
                      'install_tachyon={}'.format(
            form.cluster_name.data, form.sl_ssh_key.data,
            form.sl_domain.data,
            form.sl_datacenter.data, form.num_workers.data,
            form.sl_cpus.data, form.sl_memory.data,
            form.sl_disk_capacity.data, form.sl_network_speed.data,
            form.install_spark.data, form.install_mpi.data,
            form.install_mapred.data, form.install_mesos.data,
            form.install_hive.data, form.install_cassandra.data,
            form.install_tachyon.data
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

        components = Components(
            install_spark=form.install_spark.data,
            install_mpi=form.install_mpi.data,
            install_mapred=form.install_mapred.data,
            install_mesos=form.install_mesos.data,
            install_hive=form.install_hive.data,
            install_cassandra=form.install_cassandra.data,
            install_tachyon=form.install_tachyon.data
        )

        cluster_id = create_cluster(owner_id, sl_config, components,
                                    form.cluster_name.data)

        return redirect('/cluster_status?cluster_id={}'.format(cluster_id))

    #else:
    #    flash("Please correct errors")

    return render_template('form.html', title='Create Cluster', form=form,
                           username=session["username"])


@app.route('/view', methods=['POST', 'GET'])
def _view():
    if not logged_in():
        return redirect('/')

    cluster_id = request.args.get('cluster_id')

    cluster = Cluster.by_uuid(cluster_id)
    components = pickle.loads(cluster.components)

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
                           master_password=cluster.master_password,
                           components=components
    )


@app.route('/delete', methods=['POST', 'GET'])
def _delete():
    if not logged_in():
        return redirect('/')

    cluster_id = request.args.get('cluster_id')

    destroy_cluster(cluster_id)

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

    cluster = Cluster.by_uuid(cluster_id)
    refresh_interval = 1000

    return render_template('cluster_status.html',
                           cluster_id=cluster_id,
                           cluster_state=cluster.cluster_state,
                           refresh_interval=refresh_interval,
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
