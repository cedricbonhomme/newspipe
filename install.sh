#! /usr/bin/env sh

#
# This script install all dependencies for pyAggr3g470r.
# psycopg2 is removed from the requirements.txt file since it is only required
# if the user wants to use Postgres. Postgres is generally used on the Heroku
# platform.
#

sudo apt-get install python libpq-dev python-dev python-pip build-essential git
sudo apt-get install libxml2-dev libxslt1-dev # for lxml

sed -i '/psycopg2/d' requirements.txt
sudo pip install --upgrade -r requirements.txt

cp conf/conf.cfg-sample conf/conf.cfg
