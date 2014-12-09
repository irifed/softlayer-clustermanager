#!/bin/bash

sudo docker run -t -i -p 80:5000 \
    -v /opt/vagrant-cluster:/opt/vagrant-cluster \
    -v /var/clusters:/var/clusters \
    -v /opt/softlayer-clustermanager:/opt/softlayer-clustermanager \
    -v /opt/softlayer-clustermanager/sftlyr.pem:/root/.ssh/sftlyr.pem \
    irifed/flask_vagrant_ansible \
    /opt/softlayer-clustermanager/run.py
#   /bin/bash
