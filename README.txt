Required packages:
apache2 php5 mysql-client mysql-server vsftpd
libblas-dev liblapack-dev python-dev libatlas-base-dev gfortran python-setuptools python-scipy python-matplotlib
python-mysqldb
MySQL-python
libmysqlclient-dev

Note: Wiringpi, originating from: git clone git://git.drogon.net/wiringPi

Crontab entry for GraphTH.py:
Reads and plots latest values, transmis the plots to the local webserver. Runs every 5 minutes.
Reads ComputerTime,Temperature,Humidity entries from table TempHumid
Creates 4 different plots (30 min, 24h, 1 month, 1 year)

crontab -e
*/5 * * * * python /home/andreas/GraphTH/GraphTH.py >> /home/andreas/GraphTH.log

th.c:
make th

Ensures that th application is started on boot:
etc/rc.local:
sleep 10
/home/andreas/GraphTH/th >> /home/andreas/GraphTH/th.log &

db_pass.conf:
Contains the username and password to the local database, used by both the Python application and th.c
