#!/bin/bash

# Installation of PostgreSQL
sudo apt-get install postgresql postgresql-server-dev-9.1 postgresql-client

# Python dependencies
sudo apt-get install -y python-pip
pip install --user virtualenv
virtualenv --no-site-packages ./env_pyAggr3g470r
source ./env_pyAggr3g470r/bin/activate
pip install --upgrade -r requirements.txt

# Configuration
cp conf/conf.cfg-sample conf/conf.cfg
python db_create.py

# Launch pyAggr3g470r
python runserver.py

deactivate
