#!/usr/bin/env python

import shutil
import os
import threading
import logging
import uuid
from time import sleep

from asyncproc import Process
from sl_config import SLConfig


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s: %(levelname)s: %(filename)s: %(funcName)s(): %(message)s')
logger = logging.getLogger("handle_provisioning")


# stolen from http://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
def runProcess(command):
    myProc = Process(command)
    outf = open('vagrant.out', 'w')
    errf = open('vagrant.err', 'w')
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
        if poll != None and out == '':
            break

        if "master: SSH address:" in out:
            masterip = out.strip().split(" ")[3]
            print "MASTER IP IS: " + masterip

            # print myProc.__exitstatus

        sleep(2)

    outf.close()
    errf.close()

    return masterip


def writeCurFolderToDatabase(curdir):
    #stuff
    a = 1


def writeMasterIpToDatabase(masterip):
    #stuff
    a = 1


def handlepProcessAndWrite(runcommand, curdir):
    writeCurFolderToDatabase(curdir)
    masterip = runProcess(runcommand)
    writeMasterIpToDatabase(masterip)


def asyncRunProcess(runcommand, curdir):
    """execute following on a new thread
    handlepProcessAndWrite(runcommand, curdir)
    """

    processArgs = (runcommand, curdir)
    t = threading.Thread(target=handlepProcessAndWrite, name='cucumber',
                         args=processArgs)
    t.daemon = False
    t.start()


def do_provisioning(cluster_id, cleanrepo, vagrantroot, sl_config, num_workers):
    curdir = vagrantroot + '.' + cluster_id
    shutil.copytree(cleanrepo, curdir, symlinks=False, ignore=None)
    os.chdir(curdir)

    sl_config.create_sl_config_file(curdir + '/sl_config.yml')

    runcommand = \
        "NUM_WORKERS={} vagrant up --provider=softlayer --no-provision && " \
        "PROVIDER=softlayer vagrant provision".format(num_workers)
    logger.debug(runcommand)

    asyncRunProcess(runcommand, curdir)


def provision_cluster():
    cluster_id = str(uuid.uuid4())

    ## git clone https://github.com/irifed/vagrant-cluster.git cleanrepo
    cleanrepo = '/tmp/vagrant-cluster'
    vagrantroot = '/tmp/clusters/cluster'

    sl_config = SLConfig(
        sl_username='i.fedulova',
        sl_api_key='6941affacdc0c6bb60ac7dc2886b548462da32587ae4cdca7307ff6ea2b3a14c',
        sl_ssh_key='irina@ru.ibm.com',
        sl_private_key_path='~/.ssh/sftlyr.pem',
        sl_domain='appdirect.irina.com',
        sl_datacenter='dal06'
    )

    num_workers = 0

    do_provisioning(cluster_id, cleanrepo, vagrantroot, sl_config, num_workers)


if __name__ == "__main__":
    provision_cluster()