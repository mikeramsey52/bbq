#!/usr/bin/python3

import hbmqtt
import time
import datetime

import bbqlabels
title=bbqlabels.pagetitle
label=bbqlabels.labels

def on_temp_message(client, userdata, message):
    msg = message.payload.decode("utf-8")
    tempmsg = float(msg)
    probe = int(message.topic.split('/')[3])
    print ('probe',probe,'temp',tempmsg)
    temp[probe] = tempmsg

def on_state_message(client, userdata, message):
    statemsg = message.payload.decode("utf-8")
    probe = int(message.topic.split('/')[3])
    print ('probe',probe,'state',statemsg)
    state[probe] = statemsg


def on_action_message(client, userdata, message):
    actmsg = message.payload.decode("utf-8")
    probe = int(message.topic.split('/')[3])
    print ('probe',probe,'action',actmsg)
    action[probe] = actmsg

def mkpage():
    outfile = '/home/pi/public_html/bbq.html'
    upd = datetime.datetime.now().strftime("Updated %a %H:%M:%S")

    f = open(outfile,'w')
    f.write('<meta http-equiv="refresh" content="10">')
    f.write('<center>')
    f.write('<h1>'+title+'</h1>')
    f.write('<h2>'+upd+'</h2>')
    f.write('<table>')
    f.write('<th>')
    f.write('Probe')
    f.write('</th>')
    f.write('<th>')
    f.write('Temperature')
    f.write('</th>')
    f.write('<th>')
    f.write('Condition')
    f.write('</th>')
    f.write('<th>')
    f.write('Action')
    f.write('</th>')
    for probe in range(0,6):
        f.write('<tr>')
        f.write('<td>')
        f.write(label[probe])
        f.write('</td>')
        f.write('<td>')
        f.write(str(temp[probe]))
        f.write('</td>')
        f.write('<td>')
        f.write(state[probe])
        f.write('</td>')
        f.write('<td>')
        f.write(action[probe])
        f.write('</td>')
        f.write('</tr>')

    f.write('</table>')
    f.write('<img src="http://swing/~pi/bbq.png">')
    f.write('</center>')
   
statetopic = 'state/bbq/brisket/+/state/announce'
temptopic = 'state/bbq/brisket/+/temperature/announce'
acttopic = 'state/bbq/brisket/+/action/announce'
state = {}
temp = {}
action = {}

for probe in (0,1,2,3,4,5):
    state[probe] = 'None'
    temp[probe] = 0
    action[probe] = 'None'

hbclient = hbmqtt.hbclient()
hbclient.subscribe(statetopic,on_state_message)
hbclient.subscribe(temptopic,on_temp_message)
hbclient.subscribe(acttopic,on_action_message)
hbclient.connect()

hbclient.startloop()

while True:
    #print("page")
    mkpage()
    time.sleep(10)


