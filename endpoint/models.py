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
    email = db.Column(db.String(100))
    first = db.Column(db.String(100))
    last = db.Column(db.String(100))
    openid = db.Column(db.String(100))
    # TODO subscription = db.ReferenceProperty(CompanySubscription)
 
class Event(db.Model):
    __tablename__ = 'Event'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.DateTime)
    token = db.Column(db.String(100))
    status = db.Column(db.String(100))
    result = db.Column(db.String(100))
