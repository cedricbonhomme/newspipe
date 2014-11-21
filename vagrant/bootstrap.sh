#!/bin/sh

apt-get update
apt-get upgrade
apt-get install -y python libpq-dev python-dev python-pip git

# Clone the source code of pyAggr3g470r
git clone https://bitbucket.org/cedricbonhomme/pyaggr3g470r.git
if [ $? -ne 0 ]; then
    echo "\nERROR: unable to clone the git repository\n"
    exit 1;
fi

# Install all requierements
cd pyaggr3g470r
apt-get install -y libxml2-dev libxslt1-dev
sudo pip install --upgrade -r requirements.txt
cp vagrant/conf.cfg-sample conf/conf.cfg
cd ..

# Installation of PostgreSQL
apt-get install -y postgresql postgresql-server-dev-9.3 postgresql-client

# Configuration of the database
echo "127.0.0.1:5432:aggregator:vagrant:xxYzToW42" > .pgpass
chmod 700 .pgpass
sudo -u postgres createuser vagrant --no-superuser --createdb --no-createrole
sudo -u vagrant createdb aggregator --no-password
echo "ALTER USER vagrant WITH ENCRYPTED PASSWORD 'xxYzToW42';" | sudo -u postgres psql
echo "GRANT ALL PRIVILEGES ON DATABASE aggregator TO vagrant;" | sudo -u postgres psql

# Initializes the database
cd pyaggr3g470r
chown -R vagrant:vagrant .
sudo -u vagrant python db_create.py

# start pyAggr3g470r at startup
echo "#!/bin/sh -e" > /etc/rc.local
echo "cd /home/vagrant/pyaggr3g470r/" >> /etc/rc.local
echo "sudo -u vagrant python runserver.py &" >> /etc/rc.local
echo "exit 0" >> /etc/rc.local
chmod 755 /etc/rc.local

# Start the application.
/etc/init.d/rc.local start
