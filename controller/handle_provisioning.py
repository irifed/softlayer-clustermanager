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

import SoftLayer

from endpoint import app
from models.models import db, Cluster


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(filename)s: %(funcName)s(): %(message)s')
logger = logging.getLogger("handle_provisioning")


# # git clone --recursive https://github.com/irifed/vagrant-cluster.git cleanrepo
cleanrepo = '/opt/vagrant-cluster'
vagrantroot = '/var/clusters/cluster'


def extract_master_ip(output):
    master_ip = re.search(
        'master: SSH address: ([0-9]+(?:\.[0-9]+){3})',
        output).groups()[0]
    return master_ip


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
    masterip = None

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
            line = stdout_queue.get()
            line = line.decode(encoding='UTF-8')
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

        # Show what we received from standard error.
        while not stderr_queue.empty():
            line = stderr_queue.get()
            line = line.decode(encoding='UTF-8')
            print('STDERR: {}\n'.format(repr(line)))
            errf.write(line)
            errf.flush()

        # Sleep a bit before asking the readers again.
        time.sleep(2)

    # Let's be tidy and join the threads we've started.
    stdout_reader.join()
    stderr_reader.join()

    # Close subprocess' file descriptors.
    process.stdout.close()
    process.stderr.close()

    outf.close()
    errf.close()

    return masterip


def async_run_process(runcommand, cluster_id):
    """execute following on a new thread
    handlepProcessAndWrite(runcommand, curdir)
    """

    process_args = (runcommand, cluster_id)
    t = threading.Thread(target=run_process, name='cucumber',
                         args=process_args)
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


def async_suspend_cluster(cluster_id):
    curdir = vagrantroot + '.' + cluster_id
    os.chdir(curdir)

    runcommand = 'vagrant suspend'
    logger.debug(runcommand)

    async_run_process(runcommand, cluster_id)

    # TODO when cluster is suspended, set state in Cluster table


def async_resume_cluster(cluster_id):
    curdir = vagrantroot + '.' + cluster_id
    os.chdir(curdir)

    runcommand = 'vagrant resume'
    logger.debug(runcommand)

    async_run_process(runcommand, cluster_id)

    # TODO when cluster is resumed, set state in Cluster table


def get_cluster_status(cluster_id):
    cluster_home = vagrantroot + '.' + cluster_id

    stdout = open(cluster_home + '/vagrant.out', 'r')
    stderr = open(cluster_home + '/vagrant.err', 'r')

    cluster_log = stdout.read()
    cluster_err = stderr.read()

    master_ip = ''
    if 'master: SSH address:' in cluster_log:
        master_ip = extract_master_ip(cluster_log)

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
