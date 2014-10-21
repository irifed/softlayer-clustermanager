#!/usr/bin/env python


"""Database models used for the AppDirect sample Python application

  User: Users will belong to a company and can use the application
  Company: Companies will have subscriptions to applications
  Event: Events represent state changes in subscriptions or user assignments
"""

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class CompanySubscription(db.Model):
    __tablename__ = 'CompanySubscription'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    edition = db.Column(db.String(100))
    name = db.Column(db.String(200))
    website = db.Column(db.String(1200))


class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #email = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100))
    first = db.Column(db.String(100))
    last = db.Column(db.String(100))
    #openid = db.Column(db.String(100), unique=True)
    openid = db.Column(db.String(100))
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


class Event(db.Model):
    __tablename__ = 'Event'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    token = db.Column(db.String(100))
    status = db.Column(db.String(100))
    result = db.Column(db.String(100))


class Cluster(db.Model):
    __tablename__ = 'Cluster'
    uuid = db.Column(db.String(100), primary_key=True)
    num_workers = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('User.id'))

    def __init__(self, uuid, num_workers, owner_id):
        self.uuid = uuid
        self.num_workers = num_workers
        self.owner_id = owner_id

    @classmethod
    def by_uuid(cls, uuid):
        return db.query(cls).filter(cls.uuid == uuid).first()
