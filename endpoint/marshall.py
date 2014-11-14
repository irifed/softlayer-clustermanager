#!/usr/bin/env python

from xml.dom.minidom import Document

from models.models import User
from models.models import CompanySubscription


class EventXml(Document):
    eventXml = None
    eventType = None
    creator = None
    payload = None
    prettyPrint = ""

    def __init__(self, xmlDocument):
        super().__init__()
        self.eventXml = xmlDocument
        self.eventType = self.eventXml.getElementsByTagName('type')[0] \
            .childNodes[0].data
        self.creator = UserXml(self.eventXml, field="creator")
        self.payload = PayloadXml(self.eventXml)
        self.prettyPrint = xmlDocument.toprettyxml()

    def __str__(self):
        return self.prettyPrint


class UserXml(Document):
    userXml = None
    openid = None
    email = None
    firstName = None
    lastName = None

    def __init__(self, xmlDocument, field="user"):
        super().__init__()
        elements = xmlDocument.getElementsByTagName(field)
        if len(elements) == 0:
            return
        self.userXml = elements[0]
        self.openid = self.userXml.getElementsByTagName("openId")[0] \
            .childNodes[0].data
        self.openid = self.openid.split('/')[-1]
        self.email = self.userXml.getElementsByTagName("email")[0] \
            .childNodes[0].data
        self.firstName = self.userXml.getElementsByTagName("firstName")[0] \
            .childNodes[0].data
        self.lastName = self.userXml.getElementsByTagName("lastName")[0] \
            .childNodes[0].data

    def __str__(self):
        return self.email

    """Creates a datastore model"""
    def CreateUserModel(self, companySubscription):
        user = User.get_or_insert(self.openid)
        user.email = self.email
        user.openid = self.openid
        user.first = self.firstName
        user.last = self.lastName
        user.subscription = companySubscription
        return user


class OrderXml(Document):
    orderXml = None
    edition = None

    def __init__(self, xmlDocument):
        super().__init__()
        elements = xmlDocument.getElementsByTagName('order')
        if len(elements) == 0:
            return
        self.orderXml = elements[0]
        self.edition = self.orderXml.getElementsByTagName("editionCode")[0] \
            .childNodes[0].data

    def __str__(self):
        return self.edition


class PayloadXml(Document):
    payloadXml = None
    account = None
    user = None
    order = None
    company = None

    def __init__(self, xmlDocument):
        super().__init__()
        elements = xmlDocument.getElementsByTagName('payload')
        if len(elements) == 0:
            return
        self.payloadXml = elements[0]
        self.account = AccountXml(self.payloadXml)
        self.user = UserXml(self.payloadXml)
        self.order = OrderXml(self.payloadXml)
        self.company = CompanyXml(self.payloadXml)

    def CreateSubscription(self):
        companySubscription = CompanySubscription()
        companySubscription.edition = self.order.edition
        companySubscription.name = self.company.name
        companySubscription.website = self.company.website
        return companySubscription


class CompanyXml(Document):
    companyXml = None
    name = None
    website = None

    def __init__(self, xmlDocument):
        super().__init__()
        elements = xmlDocument.getElementsByTagName('company')
        if len(elements) == 0:
            return
        self.companyXml = elements[0]
        self.name = self.companyXml.getElementsByTagName('name')[0].childNodes[
            0].data
        self.website = \
        self.companyXml.getElementsByTagName('website')[0].childNodes[0].data

    def __str__(self):
        return self.name


class AccountXml(Document):
    accountXml = None
    accountIdentifier = None

    def __init__(self, xmlDocument):
        super().__init__()
        elements = xmlDocument.getElementsByTagName('account')
        if len(elements) == 0:
            return
        self.accountXml = elements[0]
        self.accountIdentifier = self.accountXml \
            .getElementsByTagName('accountIdentifier')[0].childNodes[0].data

    def __str__(self):
        return self.accountIdentifier
