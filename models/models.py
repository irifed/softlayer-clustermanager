#!/usr/bin/env python

"""Database models used for the AppDirect sample Python application

  User: Users will belong to a company and can use the application
  Company: Companies will have subscriptions to applications
  Event: Events represent state changes in subscriptions or user assignments
"""

import logging
logger = logging.getLogger("views")

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True)
    first = db.Column(db.String(100))
    last = db.Column(db.String(100))
    openid = db.Column(db.String(100), unique=True)
    clusters = db.relationship('Cluster', backref='owner', lazy='dynamic')

    @classmethod
    def by_openid(cls, openid):
        return cls.query.filter(cls.openid == openid).first().id

    @classmethod
    def get_or_insert(cls, openid):
        user = cls.query.filter(cls.openid == openid).first()
        if user is None:
            user = User()
        return user


class Cluster(db.Model):
    __tablename__ = 'Cluster'
    uuid = db.Column(db.String(100), primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('User.id'))

    num_workers = db.Column(db.Integer)
    cpus = db.Column(db.Integer)
    memory = db.Column(db.Integer)
    disk_capacity = db.Column(db.Integer)
    network_speed = db.Column(db.Integer)

    sl_username = db.Column(db.String(100))
    sl_api_key = db.Column(db.String(100))

    sl_ssh_key = db.Column(db.String(100))

    sl_domain = db.Column(db.String(100))
    sl_datacenter = db.Column(db.String(100))

    master_ip = db.Column(db.String(20))
    master_password = db.Column(db.String(20))

    cluster_name = db.Column(db.String(100))

    # provisioning, running, paused, destroyed (if we want to keep info about destroyed)
    cluster_state = db.Column(db.String(100))

    def __init__(self, uuid, owner_id, num_workers=5, cpus=4, memory=16384,
                 disk_capacity=100,
                 network_speed=1000,
                 sl_username='i.fedulova',
                 sl_api_key='6941affacdc0c6bb60ac7dc2886b548462da32587ae4cdca7307ff6ea2b3a14c',
                 sl_ssh_key='irina@ru.ibm.com',
                 sl_domain='irina.com',
                 sl_datacenter='dal06',
                 master_ip='0.0.0.0',
                 master_password='',
                 cluster_name='pizza',
                 cluster_state='Provisioning'):
        self.uuid = uuid
        self.owner_id = owner_id

        self.num_workers = num_workers
        self.cpus = cpus
        self.memory = memory

        self.disk_capacity = disk_capacity
        self.network_speed = network_speed

        self.sl_username = sl_username
        self.sl_api_key = sl_api_key
        self.sl_ssh_key = sl_ssh_key
        self.sl_domain = sl_domain
        self.sl_datacenter = sl_datacenter

        self.master_ip = master_ip
        self.master_password = master_password

        self.cluster_name = cluster_name
        self.cluster_state = cluster_state

    @classmethod
    def by_uuid(cls, uuid):
        return cls.query.filter(cls.uuid == uuid).first()

    @classmethod
    def by_openid(cls, openid):
        # TODO return all clusters
        logger.debug('looking for clusters owned by user with openid="{}"'.format(openid))
        count = User.query.filter(User.openid == openid).count()
        if count == 1:
            owner_id = User.query.filter(User.openid == openid).first().id
            return cls.query.filter(cls.owner_id == owner_id).first().uuid
        else:
            # no user found or multiple users found
            return None

    @classmethod
    def by_owner_id(cls, owner_id):
        return cls.query.filter(cls.owner_id == owner_id)
