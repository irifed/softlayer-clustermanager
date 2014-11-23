#!/bin/bash

# Build Docker image based on Phusion and including Python Flask, Vagrant and Ansible.
# This image is publicly available in Dockerhub,
# so there is no need to run docker-build.sh every time.
# docker-build is necessary only if additional dependency is required in image,
# e.g. additional python package.

sudo docker build -t "irifed/flask_vagrant_ansible" .

