FROM phusion/baseimage:0.9.15
MAINTAINER Irina Fedulova <fedulova@gmail.com>

# Use baseimage-docker's init system.
# CMD ["/sbin/my_init"]

RUN apt-get update && apt-get install -y python-dev python-pip python3-pip sqlite3 wget git

# Ansible requires Python 2.4+
RUN pip install ansible

# The rest of our app works under Python 3
RUN pip3 install SoftLayer
RUN pip3 install Flask Flask-OpenID gunicorn Flask-SQLAlchemy python-oauth2 pyzmq tornado WTForms flask-wtf

# Install Vagrant
WORKDIR /tmp
RUN wget https://dl.bintray.com/mitchellh/vagrant/vagrant_1.6.5_x86_64.deb
RUN dpkg -i vagrant_1.6.5_x86_64.deb
RUN vagrant plugin install vagrant-softlayer

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

