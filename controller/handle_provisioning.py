#!/usr/bin/env python

import shutil
import os
import re
import threading
import logging
import subprocess
import collections
from queue import Queue
import time
import traceback

import SoftLayer

from views import app
from models.models import db, Cluster


logger = logging.getLogger('clustermanager')

# # git clone --recursive https://github.com/irifed/vagrant-cluster.git cleanrepo
cleanrepo = '/opt/vagrant-cluster'
vagrantroot = '/var/clusters/cluster'


def extract_master_ip(output):
    master_ip = re.search(
        'master: SSH address: ([0-9]+(?:\.[0-9]+){3})',
        output).groups()[0]
    return master_ip


def remove_cluster_dir(cluster_id):
    shutil.rmtree(vagrantroot + '.' + cluster_id)
    logger.debug("deleted cluster dir = "+vagrantroot + '.' + cluster_id)

# borrowed from https://gist.github.com/soxofaan/9217628
class AsynchronousFileReader(threading.Thread):
    """
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    """

    def __init__(self, fd, queue):
        assert isinstance(queue, Queue)
        assert isinstance(fd.readline, collections.Callable)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue

    def run(self):
        """The body of the tread: read lines and put them on the queue."""
        for line in iter(self._fd.readline, b''):
            self._queue.put(line)

    def eof(self):
        """Check whether there is no more content to expect."""
        return not self.is_alive() and self._queue.empty()


def run_process(command, cluster_id):
    """
    This function runs in separate thread.
    Execute `command` in a shell.

    NOTE we call it both for provisioning and destroy, but always watch for
    master ip.
    TODO refactor this
    """

    print('RUN_PROCESS: command = {}\n'.format(command))

    # Launch the command as subprocess.
    process = subprocess.Popen(command,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True)
    outf = open('vagrant.out', 'w+')
    errf = open('vagrant.err', 'w+')

    # Launch the asynchronous readers of the process' stdout and stderr.
    stdout_queue = Queue()
    stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
    stdout_reader.start()
    stderr_queue = Queue()
    stderr_reader = AsynchronousFileReader(process.stderr, stderr_queue)
    stderr_reader.start()

    # Check the queues if we received some output (until there is nothing more to get).
    while not stdout_reader.eof() or not stderr_reader.eof():
        # Show what we received from standard output.
        while not stdout_queue.empty():
            try:
                line = stdout_queue.get().decode(encoding='ascii', errors='ignore')
                print('STDOUT: {}\n'.format(repr(line)))
                outf.write(line)
                outf.flush()

                if 'master: SSH address:' in repr(line):
                    masterip = extract_master_ip(line)
                    print('MASTER IP IS: ' + masterip)
                    store_master_ip_and_password(masterip, cluster_id)

                # hack: this is how we understand that ansible has finished
                if 'PLAY RECAP' in repr(line):
                    set_cluster_state(cluster_id, 'Running')

            except Exception:
               print(traceback.format_exc())
               print('Moving on...')

        # Show what we received from standard error.
        while not stderr_queue.empty():
            try:
                line = stdout_queue.get().decode(encoding='ascii', errors='ignore')
                print('STDERR: {}\n'.format(repr(line)))
                errf.write(line)
                errf.flush()
            except Exception:
                print(traceback.format_exc())
                print('Moving on...')

        # Sleep a bit before asking the readers again.
        time.sleep(2)

    # we are in thread, so it's okay to block
    rc = process.wait()

    # Let's be tidy and join the threads we've started.
    stdout_reader.join()
    stderr_reader.join()

    # Close subprocess' file descriptors.
    process.stdout.close()
    process.stderr.close()

    outf.close()
    errf.close()

    # at this point we know that vagrant is finished
    if command == 'vagrant destroy -f':
        remove_cluster_dir(cluster_id)


def async_run_process(runcommand, cluster_id):
    """execute following on a new thread
    handlepProcessAndWrite(runcommand, curdir)
    """

    process_args = (runcommand, cluster_id)
    t = threading.Thread(target=run_process, args=process_args)
    t.daemon = False
    t.start()


def async_provision_cluster(cluster_id, sl_config, components):
    curdir = vagrantroot + '.' + cluster_id
    shutil.copytree(cleanrepo, curdir, symlinks=False, ignore=None)
    os.chdir(curdir)

    sl_config.create_sl_config_file(curdir + '/sl_config.yml')
    components.create_components_file(
        curdir + '/ansible-bdas/group_vars/components.yml')

    runcommand = \
        "NUM_WORKERS={} vagrant up --provider=softlayer --no-provision && " \
        "PROVIDER=softlayer vagrant provision".format(sl_config.num_workers)
    logger.debug(runcommand)

    async_run_process(runcommand, cluster_id)


def async_destroy_cluster(cluster_id):
    curdir = vagrantroot + '.' + cluster_id
    os.chdir(curdir)

    runcommand = 'vagrant destroy -f'
    logger.debug(runcommand)

    async_run_process(runcommand, cluster_id)

    # TODO when cluster is destroyed, remove the containing folder


def get_cluster_status(cluster_id):
    cluster_home = vagrantroot + '.' + cluster_id
    master_ip = ''
    cluster_log = ''
    cluster_err = ''
    try:
	    stdout = open(cluster_home + '/vagrant.out', 'r')
	    stderr = open(cluster_home + '/vagrant.err', 'r')
	    cluster_log = stdout.read()
	    cluster_err = stderr.read()
	    if 'master: SSH address:' in cluster_log:
	        master_ip = extract_master_ip(cluster_log)
    except FileNotFoundError:
	    stdout = open(cluster_home + '/vagrant.out', 'a').close()
	    stderr = open(cluster_home + '/vagrant.err', 'a').close()
	    logger.debug("no vagrant.out & err files")
    finally:
	    return master_ip, cluster_log, cluster_err


def get_master_password_from_sl(master_ip, cluster_id):
    # This function executes one time from Thread and does not have db context

    if master_ip == '':
        return ''

    with app.test_request_context():
        # retrieve sl username and api key by cluster_id
        cluster = Cluster.by_uuid(cluster_id)

        logger.debug(
            'cluster_id={}, sl_username={}, master_ip={}'.format(cluster_id,
                                                                 cluster.sl_username,
                                                                 master_ip))

        client = SoftLayer.Client(username=cluster.sl_username,
                                  api_key=cluster.sl_api_key)

        vs_manager = SoftLayer.managers.VSManager(client)

        try:
            master_details = vs_manager.list_instances(public_ip=master_ip)
            if len(master_details) > 1:
                logger.error(
                    'SoftLayer API returned non-unique instance for ip = {}'.format(
                        master_ip))

            master_id = master_details[0]['id']
            master_instance = vs_manager.get_instance(instance_id=master_id)
            master_password = \
                master_instance['operatingSystem']['passwords'][0]['password']
            # store password in db for faster retrieval in the future
            cluster.master_password = master_password
            db.session.commit()

        except Exception:
            master_password = ''

        return master_password


def store_master_ip_and_password(master_ip, cluster_id):
    # TODO verify that master_ip is valid ip

    master_password = get_master_password_from_sl(master_ip, cluster_id)

    with app.test_request_context():
        cluster = Cluster.by_uuid(cluster_id)
        cluster.master_ip = master_ip
        cluster.master_password = master_password
        db.session.commit()


def set_cluster_state(cluster_id, state):
    logger.debug('setting cluster state {} for id = {}'.format(
        cluster_id, state
    ))
    with app.test_request_context():
        cluster = Cluster.by_uuid(cluster_id)

        cluster.cluster_state = state
        db.session.commit()
