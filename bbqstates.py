#!/usr/bin/python3

import hbmqtt
import pushphone
import bbqlabels

def on_message(client, userdata, message):
    msg = message.payload.decode("utf-8")
    temp = float(msg)
    probe = int(message.topic.split('/')[3])
    print ('probe',probe,'temp',temp)
    next_state(probe,temp)

def on_set_message(client, userdata, message):
    setmsg = message.payload.decode("utf-8")
    probe = int(message.topic.split('/')[3])
    print ('probe',probe,'set',setmsg)
    state[probe] = setmsg

bbqtopic = 'device/bbq/sensor/+/temperature/announce'
settopic = 'state/bbq/brisket/+/state/set'
brisketfmt = 'state/bbq/brisket/%d/state/announce'
tempfmt = 'state/bbq/brisket/%d/temperature/announce'
actfmt = 'state/bbq/brisket/%d/action/announce'

action={}
action['Initial']   = 'None'
action['Bark']   = 'None'
action['Spritz']   = 'Spray occasionally with ACV '
action['Stall']   = 'Check fat render. Wrap in butcher paper'
action['Wrapped']   = 'Return to smoker'
action['Finishing']   = 'None'
action['Done']   = 'Remove from smoker'
action['Cooling']   = 'None'
action['Resting']   = 'Place in cooler'
action['Ready']   = 'Serve'
action['Reheat']   = 'Reheat in oven'

action['Cold']   = 'Monitor Closely'
action['Below Target']   = 'Adjust vents'
action['At Target']   = 'None'
action['Above Target']   = 'Adjust vents'
action['Hot']   = 'Monitor Closely'

targetlo = 225
targethi = 250
targetmargin = 25
probes_at_temp = 0
probes_at_cool = 0
nprobes = 4 # number of temperature probes, excluding the smoker probe.

def send_data(pr,st,tm):
    topic = brisketfmt%(pr)
    temptopic = tempfmt%(pr)
    acttopic = actfmt%(pr)
    try:
        hbclient.publish( topic ,st)
        hbclient.publish( temptopic ,tm)
        hbclient.publish( acttopic ,action[st])
    except:
        hbclient.logerror('mqtt failed')

def send_to_phone(pr,st,tm):
    phonetitle = bbqlabels.labels[pr]
    phonetext = "Temp %d %s - %s" % (tm,st,action[st])
    pushphone.send(phonetitle,phonetext)

def next_state(probe,temp):
    global targetlo
    global targethi
    global targetmargin
    global probes_at_temp
    global probes_at_cool
    if temp == last_temp[probe]:
        temp_cnt[probe] = temp_cnt[probe] + 1
    else:
        last_temp[probe] = temp
        temp_cnt[probe] = 1

    next = None
    if probe == smoker:
        if state[probe] != 'Cold' and temp < targetlo - targetmargin:
            next = 'Cold'
        if state[probe] != 'Below Target' and temp < targetlo and temp >= targetlo - targetmargin:
            next = 'Below Target'
        if state[probe] != 'At Target' and temp <= targethi and temp >= targetlo :
            next = 'At Target'
        if state[probe] != 'Above Target' and temp > targethi and temp <= targethi + targetmargin:
            next = 'Above Target'
        if state[probe] != 'Hot' and temp > targethi + targetmargin:
            next = 'Hot'
    else:
        if state[probe] == 'Initial' and temp > 100:
            next = 'Bark'
        if state[probe] == 'Bark' and temp > 135:
            next = 'Spritz'
        if state[probe] == 'Spritz' and temp >= 150 and temp_cnt[probe] >= 3:
            next = 'Stall'
            stall[probe] = temp
            probes_at_temp = probes_at_temp + 1
            if probes_at_temp == nprobes:
                targetlo = 250
                targethi = 275
        if state[probe] == 'Stall' and temp < stall[probe]-25:
            next = 'Wrapped'
        if state[probe] == 'Wrapped' and temp >= stall[probe]:
            next = 'Finishing'
        if state[probe] == 'Finishing' and temp >= 203:
            next = 'Done'
        if state[probe] == 'Done' and temp < 200:
            next = 'Cooling'
            probes_at_cool = probes_at_cool + 1
            if probes_at_cool == nprobes:
                targetlo = 150
                targethi = 170
                targetmargin = 10
        if state[probe] == 'Cooling' and temp < 180:
            next = 'Resting'
        if state[probe] == 'Resting' and temp < 165:
            next = 'Ready'
        if state[probe] == 'Ready' and temp < 145:
            next = 'Reheat'
        if state[probe] == 'Reheat' and temp > 150:
            next = 'Ready'

    if next is not None:
        print('state change',probe,next)
        state[probe] = next
        send_to_phone(probe,state[probe],temp)
    send_data(probe,state[probe],temp)

hbclient = hbmqtt.hbclient()
hbclient.subscribe(bbqtopic,on_message)
hbclient.subscribe(settopic,on_set_message)
hbclient.connect()

smoker = 0
state = {}
state[smoker] = 'Cold'
last_temp = {}
last_temp[smoker] = 0
temp_cnt = {}
temp_cnt[smoker]=0
stall = {}
stall[smoker]=0
for probe in (1,2,3,4,5):
    state[probe] = 'Initial'
    last_temp[probe] = 0
    temp_cnt[probe]=0
    stall[probe]=0

for probe in (0,1,2,3,4,5):
    send_data(probe,state[probe],last_temp[probe])

hbclient.loop_forever()

