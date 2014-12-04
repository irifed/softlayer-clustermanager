#!/bin/bash

# pull changes to vagrant-cluster
pushd /opt/vagrant-cluster
git submodule foreach git pull origin master
popd

# pull changes to appdirect-bdas
pushd /opt/appdirect-bdas
git pull origin master
popd

# restart ./docker-run.sh
