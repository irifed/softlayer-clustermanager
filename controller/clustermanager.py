import logging
import uuid

from models.models import db, Cluster
from controller.handle_provisioning import provision_cluster

logger = logging.getLogger("endpoint")


def create_cluster(owner_id, sl_config):
    cluster_id = str(uuid.uuid4())

    logger.info('Creating cluster id = {}'.format(cluster_id))

    logfile = open('create_cluster.log', 'a')
    logfile.write('Created cluster {}\n'.format(cluster_id))

    # TODO store all cluster parameters, not only num_workers (?)
    cluster = Cluster(uuid=cluster_id, owner_id=owner_id, num_workers=sl_config.num_workers)
    db.session.add(cluster)
    db.session.commit()

    ## DEBUG
    # cmd = 'sl vs create -y --hourly --datacenter=dal06 --cpu=4 --memory=16384 --os=UBUNTU_LATEST --domain=bdasmarket.irina.com --hostname=controller --wait=86400 --key=irina@ru.ibm.com'
    # p = Popen(cmd, shell=True, bufsize=10000, stdin=PIPE, stdout=logfile, stderr=STDOUT)
    ## END DEBUG

    provision_cluster(cluster_id, sl_config)

    return cluster_id


def destroy_cluster(cluster_id):
    logger.info('Destroying cluster id = {}'.format(cluster_id))
    logfile = open('create_cluster.log', 'a')
    logfile.write('Destroyed cluster {}\n'.format(cluster_id))

    logger.debug('removing cluster {} from table Cluster'.format(cluster_id))
    cluster = Cluster.by_uuid(cluster_id)
    db.session.delete(cluster)
    db.session.commit()

    # TODO call vagrant destroy for this cluster


def get_master_password(master_ip, owner_id):
    pass