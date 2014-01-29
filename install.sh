#!/bin/bash

# Installation of MongoDB
sudo apt-get install -y mongodb-server
sudo service mongodb start

# Python dependencies
sudo apt-get install -y python-pip
pip install --user virtualenv
virtualenv --no-site-packages ./env_pyAggr3g470r
source ./env_pyAggr3g470r/bin/activate
pip install --upgrade -r requirements.txt
deactivate

# Configuration
cp conf/conf.cfg-sample conf/conf.cfg
python pyaggr3g470r/initialization.py pyaggr3g470r firstname lastname firstname.lastname@gmail.com secret
