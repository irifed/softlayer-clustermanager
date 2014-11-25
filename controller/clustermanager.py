import logging
import uuid


from models.models import db, Cluster
from .handle_provisioning import async_provision_cluster, async_destroy_cluster


logger = logging.getLogger("endpoint")


def create_cluster(owner_id, sl_config, cluster_name):
    cluster_id = str(uuid.uuid4())

    logger.info('Creating cluster id = {}'.format(cluster_id))

    logfile = open('create_cluster.log', 'a')
    logfile.write('Created cluster {}\n'.format(cluster_id))

    cluster = Cluster(
        uuid=cluster_id,
        owner_id=owner_id,
        cluster_name=cluster_name,
        num_workers=sl_config.num_workers,
        cpus=sl_config.cpus,
        memory=sl_config.memory,
        disk_capacity=sl_config.disk_capacity,
        network_speed=sl_config.network_speed,

        sl_username=sl_config.sl_username,
        sl_api_key=sl_config.sl_api_key,
        # TODO sl_ssh_keys
        sl_domain=sl_config.sl_domain,
        sl_datacenter=sl_config.sl_datacenter
    )
    db.session.add(cluster)
    db.session.commit()

    # # DEBUG
    # cmd = 'sl vs create -y --hourly --datacenter=dal06 --cpu=4 --memory=16384 --os=UBUNTU_LATEST --domain=bdasmarket.irina.com --hostname=controller --wait=86400 --key=irina@ru.ibm.com'
    # p = Popen(cmd, shell=True, bufsize=10000, stdin=PIPE, stdout=logfile, stderr=STDOUT)
    ## END DEBUG

    async_provision_cluster(cluster_id, sl_config)

    return cluster_id


def destroy_cluster(cluster_id):
    logger.info('Destroying cluster id = {}'.format(cluster_id))
    logfile = open('create_cluster.log', 'a')
    logfile.write('Destroyed cluster {}\n'.format(cluster_id))

    async_destroy_cluster(cluster_id)

    logger.debug('removing cluster {} from table Cluster'.format(cluster_id))
    cluster = Cluster.by_uuid(cluster_id)
    db.session.delete(cluster)
    db.session.commit()


def get_master_password(cluster_id):
    cluster = Cluster.by_uuid(cluster_id)
    if cluster is not None:
        return cluster.master_password
    return ''

