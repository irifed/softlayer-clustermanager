FROM phusion/baseimage:0.9.15
MAINTAINER Irina Fedulova <fedulova@gmail.com>

ENV VAGRANT_VERSION 1.7.4

# Use baseimage-docker's init system.
# CMD ["/sbin/my_init"]

RUN apt-get update 
RUN apt-get install -y python-dev python-pip python3-pip sqlite3 wget git 

# Ansible requires Python 2.4+
RUN pip install ansible

# The rest of our app works under Python 3
RUN pip3 install SoftLayer
RUN pip3 install Flask Flask-OpenID gunicorn Flask-SQLAlchemy \
                 python-oauth2 pyzmq tornado WTForms flask-wtf

# Install Vagrant
WORKDIR /tmp
RUN wget https://dl.bintray.com/mitchellh/vagrant/vagrant_${VAGRANT_VERSION}_x86_64.deb
RUN dpkg -i vagrant_${VAGRANT_VERSION}_x86_64.deb
RUN vagrant plugin install vagrant-softlayer

# Patch Vagrant to disable color in ansible log 
WORKDIR /opt/vagrant/embedded/gems/gems/vagrant-${VAGRANT_VERSION}/plugins/provisioners/ansible
RUN sed -i s/'"ANSIBLE_FORCE_COLOR" => "true",'/'"ANSIBLE_FORCE_COLOR" => "false",'/ provisioner.rb

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
