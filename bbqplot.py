#!/usr/bin/python3

# start server with "sudo systemctl start mariadb"

import sys
import mariadb
import datetime
import time
import bbqlabels

import matplotlib.pyplot as plt
import matplotlib.figure as fig
import matplotlib.dates as d2n
import matplotlib.dates as mdates
from matplotlib import rc

figfile = '/home/pi/public_html/bbq.png'

while True:

    mydate = datetime.datetime.now()
    period = datetime.timedelta(hours=24)
    period = datetime.timedelta(hours=24*5)
    start = mydate - period
    startq = start.strftime("%Y-%m-%d")
    plotdate = mydate.strftime("%b %d %H:%M")

    nprobes = 6

    temps = [ [],[],[],[],[],[] ] 
    times = [ [],[],[],[],[],[] ] 

    try:
        conn = mariadb.connect(
        user="hb",
        password="2totwomc",
        host="localhost",
        database="hb"
        )
        cursor = conn.cursor()
        query = "Select ts,probe,temp from bbq where ts > '%s'" % (startq) 
        cursor.execute( query )
        print (query)

        for (ts,probe,temp) in cursor:
            print(ts,probe,temp,type(ts))
            probe = int(probe)
            print(ts,probe,temp)
            times[probe].append(ts)
            temps[probe].append(temp)


        conn.close()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    except:
        print('other error')
    
    #for n in range(nprobes):
        #print(n,data[n]['time'])
        #print(n,times[n])

    for n in range(nprobes):
        print('n',n)
        #print(data[n]['time'])
        #d  = d2n.date2num(data[n]['time'])
        #data[n]['time'] = d
        times[n]  = d2n.date2num(times[n])
    #times  = d2n.date2num(times)
    
    myfigure = plt.figure()
    plt.style.use("fivethirtyeight")
    plt.title(bbqlabels.plottitle)
    plt.xticks(rotation=60)

    ax=myfigure.add_subplot(111)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %H:%M'))

    for n in range(nprobes):
        ax.plot_date(times[n],temps[n],xdate=True,ls='solid',label=bbqlabels.labels[n],lw=1,markersize=2)

    plt.legend(fontsize='small')

    plt.savefig(figfile, bbox_inches='tight')
    #plt.show()

    time.sleep(180)
