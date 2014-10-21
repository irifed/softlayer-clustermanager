import logging
import uuid

from models import db
from cluster import create_cluster

xml_order_ok = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<result>
    <success>true</success>
    <message>Account creation successful</message>
    <accountIdentifier>{}</accountIdentifier>
</result>'''

xml_success = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<result>
    <success>true</success>
    <accountIdentifier>{}</accountIdentifier>
</result>
'''

xml_order_error = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<result>
   <success>false</success>
   <errorCode>{}</errorCode>
   <message>{}</message>
</result>'''

def HandleEvent(event_xml):
    logging.info('Received event type {}'.format(event_xml.eventType))
    if event_xml.eventType == "SUBSCRIPTION_ORDER":
        return CreateOrder(event_xml)
    elif event_xml.eventType == "SUBSCRIPTION_CANCEL":
        return CancelOrder(event_xml)

    # TODO
    # elif event_xml.eventType == "SUBSCRIPTION_CHANGE":
    #     return ChangeOrder(event_xml)
    # elif event_xml.eventType == "USER_ASSIGNMENT":
    #     return AssignUser(event_xml)
    # elif event_xml.eventType == "USER_UNASSIGNMENT":
    #     return UnassignUser(event_xml)
    # else:
    #     message = "Event type %s is not configured" % event_xml.eventType
    #     return errorTemplate % ( "CONFIGURATION_ERROR", message)

def CreateOrder(event_xml):
    logging.info("CreateOrder {} {} {}".format(event_xml.payload.company.name,
                                    event_xml.payload.company.website,
                                    event_xml.payload.order.edition))

    companySubscription = event_xml.payload.CreateSubscription()
    db.session.add(companySubscription)

    creator = event_xml.creator.CreateUserModel(companySubscription)
    db.session.add(creator)

    cluster_id = uuid.uuid4()
    # TODO store it in the database

    # TODO fire up vagrant with unique id
    create_cluster(cluster_id)

    db.session.commit()

    return xml_order_ok.format(cluster_id)

def CancelOrder(event_xml):
    cluster_id = event_xml.payload.account.accountIdentifier
    logging.info('Destroying cluster {}'.format(cluster_id))
    # TODO verify that cluster id exists in database
    # TODO delete record from the database
    # TODO destroy cluster
    return xml_success.format(cluster_id)
