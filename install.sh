#! /usr/bin/env bash

#
# This script install all dependencies for pyAggr3g470r.
#

sudo apt-get install python libpq-dev python-dev python-pip build-essential git
sudo apt-get install libxml2-dev libxslt1-dev # for lxml

sed -i '/psycopg2/d' requirements.txt
sudo pip install --upgrade -r requirements.txt

# Initializes the configuration file
cp conf/conf.cfg-sample conf/conf.cfg

# Delete default database configuration
sed -i '/database/d' conf/conf.cfg
sed -i '/uri/d' conf/conf.cfg

if [ "$1" == postgre ]; then
    sudo apt-get install -y postgresql postgresql-server-dev-9.3 postgresql-client
    sudo pip install psycopg2
    echo "127.0.0.1:5432:aggregator:pgsqluser:pgsqlpwd" > ~/.pgpass
    chmod 700 ~/.pgpass
    sudo -u postgres createuser pgsqluser --no-superuser --createdb --no-createrole
    createdb aggregator --no-password
    echo "ALTER USER pgsqluser WITH ENCRYPTED PASSWORD 'pgsqlpwd';" | sudo -u postgres psql
    echo "GRANT ALL PRIVILEGES ON DATABASE aggregator TO pgsqluser;" | sudo -u postgres psql

    # Add configuration lines for PostgreSQL
    echo '[database]' >> conf/conf.cfg
    echo 'uri = postgres://pgsqluser:pgsqlpwd@127.0.0.1:5432/aggregator' >> conf/conf.cfg
elif [ "$1" == sqlite ]; then
    # Add configuration lines for SQLite
    echo '[database]' >> conf/conf.cfg
    echo 'uri = sqlite+pysqlite:///pyAggr3g470r.db' >> conf/conf.cfg
fi
