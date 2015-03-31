#!/bin/sh

apt-get update
apt-get upgrade
apt-get install -y python3 python3-dev libpq-dev python3-pip build-essential git

# Clone the source code of pyAggr3g470r
git clone https://bitbucket.org/cedricbonhomme/pyaggr3g470r.git
if [ $? -ne 0 ]; then
    echo "\nERROR: unable to clone the git repository\n"
    exit 1;
fi

# Installation of PostgreSQL
apt-get install -y postgresql postgresql-server-dev-9.4 postgresql-client

# Install all Python requierements
cd pyaggr3g470r
# For lxml
apt-get install -y libxml2-dev libxslt1-dev
# installation with pip
sudo pip3 install --upgrade -r requirements.txt
wget https://raw.github.com/pypa/pip/master/contrib/get-pip.py
sudo python3 get-pip.py
rm get-pip.py
sudo pip3 uninstall -y feedparser
sudo pip3 install feedparser==5.1.2
# copy of the default configuration files for vagrant
cp vagrant/conf.cfg-sample conf/conf.cfg
cd ..

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
sudo -u vagrant python3 manager.py db_empty
sudo -u vagrant python3 manager.py db_create

# start pyAggr3g470r at startup
echo "#!/bin/sh -e" > /etc/rc.local
echo "cd /home/vagrant/pyaggr3g470r/" >> /etc/rc.local
echo "sudo -u vagrant python3 runserver.py &" >> /etc/rc.local
echo "exit 0" >> /etc/rc.local
chmod 755 /etc/rc.local

# Start the application.
/etc/init.d/rc.local start


#write out current crontab
sudo -u vagrant crontab -l > mycron
#echo new cron into cron file
sudo -u vagrant echo "*/30 * * * * cd /home/vagrant/pyaggr3g470r/ ; python3 manager.py fetch_asyncio None None" >> mycron
#install new cron file
sudo -u vagrant crontab mycron
sudo -u vagrant rm mycron
