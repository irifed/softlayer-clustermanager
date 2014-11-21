#!/bin/bash

sudo docker run -t -i -p 8080:5000 \
    -v /opt/vagrant-cluster:/opt/vagrant-cluster \
    -v /var/clusters:/var/clusters \
    -v /opt/appdirect-bdas:/opt/appdirect-bdas \
    -v /opt/appdirect-bdas/sftlyr.pem:/root/.ssh/sftlyr.pem \
    irifed/flask_vagrant_ansible \
    /opt/appdirect-bdas/run.py
#   /bin/bash
