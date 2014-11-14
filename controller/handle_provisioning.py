#!/usr/bin/env python

import shutil
import os
import re
import threading
import logging
from time import sleep

from .asyncproc import Process


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(filename)s: %(funcName)s(): %(message)s')
logger = logging.getLogger("handle_provisioning")


# # git clone --recursive https://github.com/irifed/vagrant-cluster.git cleanrepo
cleanrepo = '/tmp/vagrant-cluster'
vagrantroot = '/tmp/clusters/cluster'


# stolen from http://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
def run_process(command):
    myProc = Process(command)
    outf = open('vagrant.out', 'w')
    errf = open('vagrant.err', 'w')
    masterip = None
    while True:
        # print any new output to files
        out, err = myProc.readboth()
        if out != "":
            outf.write(out)
            outf.flush()
        if err != "":
            errf.write(err)
            errf.flush()

        # check to see if process has ended
        poll = myProc.wait(os.WNOHANG)
        if poll is not None and out == '':
            break

        if "master: SSH address:" in out:
            masterip = out.strip().split(" ")[3]
            print("MASTER IP IS: " + masterip)
            write_master_ip_to_database(masterip)

            # print myProc.__exitstatus

        sleep(2)

    outf.close()
    errf.close()

    return masterip


def write_master_ip_to_database(masterip):
    #stuff
    a = 1


def handle_process_and_write(runcommand, curdir):
    masterip = run_process(runcommand)
    write_master_ip_to_database(masterip)


def async_run_process(runcommand, curdir):
    """execute following on a new thread
    handlepProcessAndWrite(runcommand, curdir)
    """

    processArgs = (runcommand, curdir)
    t = threading.Thread(target=handle_process_and_write, name='cucumber',
                         args=processArgs)
    t.daemon = False
    t.start()


def do_provisioning(cluster_id, cleanrepo, vagrantroot, sl_config):
    curdir = vagrantroot + '.' + cluster_id
    shutil.copytree(cleanrepo, curdir, symlinks=False, ignore=None)
    os.chdir(curdir)

    sl_config.create_sl_config_file(curdir + '/sl_config.yml')

    runcommand = \
        "NUM_WORKERS={} vagrant up --provider=softlayer --no-provision && " \
        "PROVIDER=softlayer vagrant provision".format(sl_config.num_workers)
    logger.debug(runcommand)

    async_run_process(runcommand, curdir)


def provision_cluster(cluster_id, sl_config):
    # TODO get rid of this function
    do_provisioning(cluster_id, cleanrepo, vagrantroot, sl_config)


def get_cluster_status(cluster_id):
    cluster_home = vagrantroot + '.' + cluster_id

    stdout = open(cluster_home + '/vagrant.out', 'r')
    stderr = open(cluster_home + '/vagrant.err', 'r')

    # TODO grep out master ip address
    cluster_log = stdout.read()
    cluster_err = stderr.read()

    master_ip = None
    if 'master: SSH address:' in cluster_log:
        master_ip = re.search(
            'master: SSH address: ([0-9]+(?:\.[0-9]+){3})',
            cluster_log).groups()[0]

    return master_ip, cluster_log, cluster_err
