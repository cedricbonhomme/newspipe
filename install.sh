#! /usr/bin/env bash

#
# This script install all dependencies and configure Newspipe.
# Usage:
# ./install.sh (sqlite|postgres)
#


sudo apt-get install npm

poetry install
npm install

cp newspipe/conf/conf.cfg-sample newspipe/conf/conf.cfg
# Delete default database configuration
sed -i '/database/d' newspipe/conf/conf.cfg
sed -i '/database_url/d' newspipe/conf/conf.cfg

# Configuration of the database
if [ "$1" == postgres ]; then
    echo "Installing requirements for PostgreSQL..."
    sudo apt-get install -y postgresql > /dev/null
    echo "Configuring the database..."
    echo "127.0.0.1:5433:aggregator:pgsqluser:pgsqlpwd" > ~/.pgpass
    chmod 0600 ~/.pgpass
    sudo -u postgres createuser pgsqluser --no-superuser --createdb --no-createrole
    sudo -u postgres createdb aggregator --no-password
    echo "ALTER USER pgsqluser WITH ENCRYPTED PASSWORD 'pgsqlpwd';" | sudo -u postgres psql
    echo "GRANT ALL PRIVILEGES ON DATABASE aggregator TO pgsqluser;" | sudo -u postgres psql

    # Add configuration lines for PostgreSQL
    echo '[database]' >> newspipe/conf/conf.cfg
    echo 'database_url = postgres://pgsqluser:pgsqlpwd@127.0.0.1:5433/aggregator' >> newspipe/conf/conf.cfg
elif [ "$1" == sqlite ]; then
    # Add configuration lines for SQLite
    echo "Configuring the SQLite database..."

    echo '[database]' >> newspipe/conf/conf.cfg
    echo 'database_url = sqlite:///newspipe.db' >> newspipe/conf/conf.cfg
fi

poetry shell

echo "Initialization of the database..."
python newspipe/manager.py db_empty
python newspipe/manager.py db_create

echo "Launching Newspipe..."
python newspipe/runserver.py
