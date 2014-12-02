import logging

from models.models import db
from models.sl_config import SLConfig
from models.components import Components
from controller.clustermanager import create_cluster, destroy_cluster


logger = logging.getLogger("endpoint")

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
</result>'''

xml_order_error = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<result>
   <success>false</success>
   <errorCode>{}</errorCode>
   <message>{}</message>
</result>'''


def HandleEvent(event_xml):
    logger.info('Received event type {}'.format(event_xml.eventType))
    if event_xml.eventType == "SUBSCRIPTION_ORDER":
        return CreateOrder(event_xml)
    elif event_xml.eventType == "SUBSCRIPTION_CANCEL":
        return CancelOrder(event_xml)

        # TODO
        # elif event_xml.eventType == "SUBSCRIPTION_CHANGE":
        # return ChangeOrder(event_xml)
        # elif event_xml.eventType == "USER_ASSIGNMENT":
        #     return AssignUser(event_xml)
        # elif event_xml.eventType == "USER_UNASSIGNMENT":
        #     return UnassignUser(event_xml)
        # else:
        #     message = "Event type %s is not configured" % event_xml.eventType
        #     return errorTemplate % ( "CONFIGURATION_ERROR", message)


def CreateOrder(event_xml):
    logger.info("CreateOrder {} {} {}".format(event_xml.payload.company.name,
                                              event_xml.payload.company.website,
                                              event_xml.payload.order.edition))

    companySubscription = event_xml.payload.CreateSubscription()
    db.session.add(companySubscription)

    creator = event_xml.creator.CreateUserModel(companySubscription)
    db.session.add(creator)
    db.session.commit()

    owner_id = creator.by_openid(creator.openid)

    # TODO get num_workers and sl_config using interactive endpoint
    sl_config = SLConfig(
        sl_username='i.fedulova',
        sl_api_key='6941affacdc0c6bb60ac7dc2886b548462da32587ae4cdca7307ff6ea2b3a14c',

        # TODO refactor hack with irina's ssh key
        sl_ssh_keys=['irina@ru.ibm.com', 'TODO user key'],
        sl_private_key_path='~/.ssh/sftlyr.pem',

        sl_domain='appdirect.irina.com',
        sl_datacenter='dal06',
        num_workers=5
    )

    # TODO get components from interactive endpoint
    components = Components()

    cluster_id = create_cluster(owner_id, sl_config, components, 'clustername')

    # return cluster_id, AppDirect will store it as accountIdentifier
    return xml_order_ok.format(cluster_id)


def CancelOrder(event_xml):
    cluster_id = event_xml.payload.account.accountIdentifier
    logger.info('CancelOrder {}'.format(cluster_id))

    destroy_cluster(cluster_id)

    return xml_success.format(cluster_id)
