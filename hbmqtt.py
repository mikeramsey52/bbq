#!/usr/bin/python3

import paho.mqtt.client as mqtt
import logging
import os
import sys
import threading
#from PyQt5.QtCore import QThread


class hbclient:
    mqttserver = 'yourmqttserver'
    pid = os.getpid()
    #clientname = os.path.basename(__file__)
    clientname,ext = os.path.splitext(os.path.basename(sys.argv[0]))
    clientid = '%s-%d' % (clientname,pid)
    subscriptions = []
    clientstat = 'state/system/client/%s/live/announce' % (clientname)
    connected = False

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    logfh = logging.FileHandler("/tmp/%s.log"%(clientname), "w")
    logger.addHandler(logfh)
    keep_fds = [logfh.stream.fileno()]
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logfh.setFormatter(formatter)

    def __init__(self,stay_alive=True): 
        self.client = mqtt.Client(self.clientid)
        self.client.on_connect=self.on_connect
        self.stay_alive = stay_alive
        if self.stay_alive:
            self.client.will_set(self.clientstat,payload=0,qos=1,retain=True)
        self.logdebug('initiated')

    def threadable(self):
        self.thread=threading.Thread(name=self.clientname,target=self.runloop)
           #args=(self))
    def startloop(self):
        self.logdebug('starting loop')
        self.client.loop_start()
    def runloop(self):
        self.client.loop_forever()
    def looponce(self):
        self.client.loop()
    def runthread(self):
        self.thread.start()
        #self.thread.run()
        

    def subscribe(self,topic,callback):
        self.subscriptions.append( (topic,callback) )
    def publish(self,topic,val):
        self.client.publish(topic,payload=val,retain=True,qos=1) 
    def signal(self,topic,val): #intended for events,signals not to be retained
        self.client.publish(topic,payload=val,qos=1) 
    def connect(self):
        self.logdebug('connecting')
        self.client.connect(self.mqttserver)
    def on_connect(self,client, userdata, flags, rc):
        self.logdebug('connected')
        for sub in self.subscriptions:
            (topic, callback) = sub
            self.logdebug('subscribing %s'%topic)
            self.client.subscribe(topic,qos=1)
            self.client.message_callback_add(topic,callback)
            print('sub loop',topic)
        if self.stay_alive:
            self.logdebug('publish %s'%self.clientstat)
            self.client.publish(self.clientstat,payload=1,qos=1,retain=True)
        self.connected = True
    def loop_forever(self):
        self.client.loop_forever()

    def seterror(self):
        self.logger.setLevel(logging.ERROR)
    def setinfo(self):
        self.logger.setLevel(logging.INFO)
    def setdebug(self):
        self.logger.setLevel(logging.DEBUG)
    def logdebug(self,message):
        #print(message)
        self.logger.debug(message)
    def logerror(self,message):
        self.logger.error(message)
    def loginfo(self,message):
        self.logger.info(message)

