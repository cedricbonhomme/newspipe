#!/bin/sh

# Installation of MongoDB
if ! dpkg -s mongodb-server | grep -i 'status' | grep -i 'installed' > /dev/null ; then
    sudo apt-get install -y mongodb-server
    sudo service mongodb start
fi

sudo apt-get install -y python-pip
pip install --user virtualenv
virtualenv --no-site-packages ./env_pyAggr3g470r
source ./env_pyAggr3g470r/bin/activate
pip install --upgrade -r requirements.txt
deactivate

cp conf/conf.cfg-sample conf/conf.cfg
