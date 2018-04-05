#! /usr/bin/env bash

#
# This script install all dependencies and configure Newspipe.
# Usage:
# ./install.sh (sqlite|postgres)
#


sudo apt-get install npm

pipenv install
npm install

cp src/conf/conf.cfg-sample src/conf/conf.cfg
# Delete default database configuration
sed -i '/database/d' src/conf/conf.cfg
sed -i '/database_url/d' src/conf/conf.cfg

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
    echo '[database]' >> src/conf/conf.cfg
    echo 'database_url = postgres://pgsqluser:pgsqlpwd@127.0.0.1:5433/aggregator' >> src/conf/conf.cfg
elif [ "$1" == sqlite ]; then
    # Add configuration lines for SQLite
    echo "Configuring the SQLite database..."

    echo '[database]' >> src/conf/conf.cfg
    echo 'database_url = sqlite:///newspipe.db' >> src/conf/conf.cfg
fi

pipenv shell

echo "Initialization of the database..."
python src/manager.py db_empty
python src/manager.py db_create

echo "Launching Newspipe..."
python src/runserver.py
