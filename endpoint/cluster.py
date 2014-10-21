from subprocess import Popen, PIPE, STDOUT
import logging

def create_cluster(cluster_id):
    logging.info('Creating cluster id={}'.format(cluster_id))
    logfile = open('create_cluster.log', 'a')

    logfile.write('Created cluster {}\n'.format(cluster_id))

    # cmd = 'sl vs create -y --hourly --datacenter=dal06 --cpu=4 --memory=16384 --os=UBUNTU_LATEST --domain=bdasmarket.irina.com --hostname=controller --wait=86400 --key=irina@ru.ibm.com'
    # p = Popen(cmd, shell=True, bufsize=10000, stdin=PIPE, stdout=logfile, stderr=STDOUT)


