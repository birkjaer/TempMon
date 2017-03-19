#
# pull data from sql, plot using matplotlib
# see http://stackoverflow.com/questions/18663746/matplotlib-multiple-lines-with-common-date-on-x-axis-solved
#
# rev 1.0 12/02/2013 WPNS built from GraphAirmuxSD.py V1.1
# rev 1.1 12/02/2013 WPNS remove large delta values
# rev 1.2 12/02/2013 WPNS remove -0.1 values (failed to read)
# rev 1.3 12/02/2013 WPNS show count of anomalies
# rev 1.4 12/03/2013 WPNS cleanup, release
# rev 1.5 12/03/2013 WPNS better label
# rev 1.6 12/03/2013 WPNS bugfix, release
# rev 1.69 12/04/2013 WPNS release to Instructables

import sys
import os
import time
import math
import datetime
import MySQLdb as mdb
import numpy

# so matplotlib has to have some of the setup parameters _before_ pyplot
import matplotlib
matplotlib.use('agg')

#matplotlib.rcParams['figure.dpi'] = 100
#matplotlib.rcParams['figure.figsize'] = [10.24, 7.68]
matplotlib.rcParams['lines.linewidth'] = 0.5
matplotlib.rcParams['axes.color_cycle'] = ['r','g','b','k']
matplotlib.rcParams['axes.labelsize'] = 'large'
matplotlib.rcParams['font.size'] = 8
matplotlib.rcParams['grid.linestyle']='-'

import matplotlib.pyplot as plt

anomalies = 0
#30 min, 24h, 1 month, 1 year
index1 = 0
index2 = 0
index3 = 0
index4 = 0

print "GraphTH.py",time.asctime(),

# open the database connection, read the last <many> seconds of data, put them in a Numpy array called Raw
DBconn = mdb.connect(host="localhost", db="Monitoring", read_default_file="/home/andreas/TempMon/db_pass.conf")
cursor = DBconn.cursor()
sql = "select ComputerTime,Temperature,Humidity from TempHumid where ComputerTime >= (unix_timestamp(now())-(60*60*24*365))"
cursor.execute(sql)
Raw = numpy.fromiter(cursor.fetchall(), count=-1, dtype=[('', numpy.float)]*3)

Raw = Raw.view(numpy.float).reshape(-1, 3)

#Go through the array, find the indexes for each of the wanted graphs (30 min, 24h, 1 month, 1 year)
entries = (Raw.size/3)-1
lastts = Raw[entries,0]
for y in range (entries, 0, -1):
    if(index1 == 0):
        if(Raw[y-1,0] < (lastts-(30*60))): #30 minute mark
            index1 = y
        continue
    elif(index2 == 0):
        if(Raw[y-1,0] < (lastts-(24*60*60))): #24 hour mark
            index2 = y
        continue
    elif(index3 == 0):
        if(Raw[y-1,0] < (lastts-(30*24*60*60))): #1 month mark
            index3 = y
        continue
    elif(index4 == 0):
        if(Raw[y-1,0] < (lastts-(365*24*60*60))): #1 year mark
            index4 = y
        continue
   
(samples,ports)=Raw.shape
print 'Samples: {}, DataPoints: {}'.format(samples,ports),

#plotme30m=numpy.zeros((samples-index1, ports-1)) # make an array the same shape minus the epoch numbers
#plotme24h=numpy.zeros((samples-index2, ports-1))
#plotme30d=numpy.zeros((samples-index3, ports-1))
#plotme01y=numpy.zeros((samples-index4, ports-1))

plotme=numpy.zeros((samples, ports-1))
for y in range(ports-1):
    for x in range(samples-1):  # can't do last one, there's no (time) delta from previous sample
        seconds = Raw[x+1,0]-Raw[x,0]
        # if the number didn't overflow the counter
        plotme[x,y] = Raw[x,y+1]

    for x in range(samples-1):                   # go thru the dataset
        if (Raw[x+1,1] == -0.1):                 # if values are "reading failed" flag
            plotme[x+1,0] = plotme[x,0]          # copy current sample over it
            plotme[x+1,1] = plotme[x,1]          # for temperature and humidity both
            anomalies += 1

        if (abs(Raw[x+1,1]-Raw[x,1]) > 10):      # if temperature jumps more than 10 degrees in a minute
            plotme[x+1,0] = plotme[x,0]          # copy current sample over it
            plotme[x+1,1] = plotme[x,1]          # for temperature and humidity both
            anomalies += 1
    

    plotme[samples-1,y] = None # set last sample to "do not plot"

print "Anomalies: ",anomalies,


plotme30m = plotme[index1:, ]
plotme24h = plotme[index2:, ]
plotme30d = plotme[index3:, ]
plotme01y = plotme[index4:, ]

# get an array of adatetime objects (askewchan from stackoverflow, above)
dts = map(datetime.datetime.fromtimestamp, Raw[:,0])
dts30m = map(datetime.datetime.fromtimestamp, Raw[index1:,0])
dts24h = map(datetime.datetime.fromtimestamp, Raw[index2:,0])
dts30d = map(datetime.datetime.fromtimestamp, Raw[index3:,0])
dts01y = map(datetime.datetime.fromtimestamp, Raw[index4:,0])

# set up the plot details we want
#30 minutes
plt.figure(1)
plt.grid(True)
plt.ylabel('Temp C, RH %%')
plt.axis(ymax=100,ymin=0)
plt.xlabel(time.asctime())
plt.title("Living Room Temperature (Red), Humidity (Green)")
plt.hold(True)

plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m/%d %H:%M'))
plt.gca().xaxis.set_major_locator(matplotlib.dates.HourLocator())
lines = plt.plot(dts24h,plotme24h)
plt.gcf().autofmt_xdate()

FileName = '/home/andreas/TempMon/graphics/LivingRoom_24h.png'
plt.savefig(FileName)

#24 hours
plt.figure(2)
plt.grid(True)
plt.ylabel('Temp C, RH %%')
plt.axis(ymax=100,ymin=0)
plt.xlabel(time.asctime())
plt.title("Living Room Temperature (Red), Humidity (Green)")
plt.hold(True)

plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m/%d %H:%M'))
plt.gca().xaxis.set_major_locator(matplotlib.dates.MinuteLocator())
lines = plt.plot(dts30m,plotme30m)
plt.gcf().autofmt_xdate()

FileName = '/home/andreas/TempMon/graphics/LivingRoom_30m.png'
plt.savefig(FileName)

#30 days
plt.figure(3)
plt.grid(True)
plt.ylabel('Temp C, RH %%')
plt.axis(ymax=100,ymin=0)
plt.xlabel(time.asctime())
plt.title("Living Room Temperature (Red), Humidity (Green)")
plt.hold(True)

plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m/%d %H:%M'))
plt.gca().xaxis.set_major_locator(matplotlib.dates.DayLocator())
lines = plt.plot(dts30d,plotme30d)
plt.gcf().autofmt_xdate()

FileName = '/home/andreas/TempMon/graphics/LivingRoom_30d.png'
plt.savefig(FileName)

#1 year
plt.figure(4)
plt.grid(True)
plt.ylabel('Temp C, RH %%')
plt.axis(ymax=100,ymin=0)
plt.xlabel(time.asctime())
plt.title("Living Room Temperature (Red), Humidity (Green)")
plt.hold(True)

plt.gca().xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m/%d %H:%M'))
plt.gca().xaxis.set_major_locator(matplotlib.dates.MonthLocator())
lines = plt.plot(dts01y,plotme01y)
plt.gcf().autofmt_xdate()

FileName = '/home/andreas/TempMon/graphics/LivingRoom_01y.png'
plt.savefig(FileName)

print 'Copy to Web Server...',
os.system("scp /home/andreas/TempMon/graphics/LivingRoom_30m.png andreas@raspmail:/var/www/photoshow/graphics/LivingRoom_30m.png")
os.system("scp /home/andreas/TempMon/graphics/LivingRoom_24h.png andreas@raspmail:/var/www/photoshow/graphics/LivingRoom_24h.png")
os.system("scp /home/andreas/TempMon/graphics/LivingRoom_30d.png andreas@raspmail:/var/www/photoshow/graphics/LivingRoom_30d.png")
os.system("scp /home/andreas/TempMon/graphics/LivingRoom_01y.png andreas@raspmail:/var/www/photoshow/graphics/LivingRoom_01y.png")
print 'Done at',time.asctime()


