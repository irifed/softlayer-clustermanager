import logging
from subprocess import Popen, PIPE, STDOUT

logger = logging.getLogger("endpoint")

def create_cluster(cluster_id):
    logger.info('Creating cluster id = {}'.format(cluster_id))
    logfile = open('create_cluster.log', 'a')

    logfile.write('Created cluster {}\n'.format(cluster_id))

    # TODO call vagrant up && vagrant provision
    # cmd = 'sl vs create -y --hourly --datacenter=dal06 --cpu=4 --memory=16384 --os=UBUNTU_LATEST --domain=bdasmarket.irina.com --hostname=controller --wait=86400 --key=irina@ru.ibm.com'
    # p = Popen(cmd, shell=True, bufsize=10000, stdin=PIPE, stdout=logfile, stderr=STDOUT)

def destroy_cluster(cluster_id):
    logger.info('Destroying cluster id = {}'.format(cluster_id))
    logfile = open('create_cluster.log', 'a')

    logfile.write('Destroyed cluster {}\n'.format(cluster_id))

    # TODO call vagrant destroy
