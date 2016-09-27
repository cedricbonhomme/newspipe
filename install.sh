#! /usr/bin/env bash

#
# This script install all dependencies and configure JARR.
# Usage:
# ./install.sh (sqlite|postgres)
#

PYTHON_VERSION="3.5"


sudo apt-get install -y build-essential git wget > /dev/null
sudo apt-get install -y libxml2-dev libxslt1-dev > /dev/null # for lxml
sudo apt-get install -y libssl-dev openssl > /dev/null # for pip


echo "Installation of Python..."
if [ "$1" == postgres ]; then
    sudo apt-get install -y libpq-dev  > /dev/null
elif [ "$1" == sqlite ]; then
    sudo apt-get install -y libsqlite3-dev  > /dev/null
fi
wget https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tar.xz -o /dev/null  > /dev/null
tar -xf Python-3.5.2.tar.xz  > /dev/null
rm Python-3.5.2.tar.xz  > /dev/null
cd Python-3.5.2/
export PYTHONHOME=/usr/local
export LD_RUN_PATH=/usr/local/lib/
echo "test:"
echo $PYTHONHOME
./configure --enable-loadable-sqlite-extensions --enable-shared  > /dev/null
make  > /dev/null
sudo make install  > /dev/null
cd ..
sudo rm -Rf Python-3.5.2/


echo "Installing required Python libraries..."
sed -i '/psycopg2/d' requirements.txt > /dev/null
sudo pip$PYTHON_VERSION install --upgrade pip
sudo pip$PYTHON_VERSION install --upgrade -r requirements.txt > /dev/null


# Initializes the configuration file
cp src/conf/conf.cfg-sample src/conf/conf.cfg
# Delete default database configuration
sed -i '/database/d' src/conf/conf.cfg
sed -i '/database_url/d' src/conf/conf.cfg


# Configuration of the database
if [ "$1" == postgres ]; then
    echo "Installing requirements for PostgreSQL..."
    sudo apt-get install -y postgresql postgresql-server-dev-9.4 postgresql-client > /dev/null
    sudo pip$PYTHON_VERSION install psycopg2 > /dev/null
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
    echo 'database_url = sqlite:///jarr.db' >> src/conf/conf.cfg
fi


echo "Initialization of the database..."
python$PYTHON_VERSION src/manager.py db_empty
python$PYTHON_VERSION src/manager.py db_create


# Bootstrap
echo "Retrieving bootstrap..."
git submodule init > /dev/null
git submodule update > /dev/null


echo "Installation terminated."
echo "Launch JARR with the command:"
echo -e "\tpython$PYTHON_VERSION src/runserver.py"
