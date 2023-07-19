#!/usr/bin/python3
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time,sys

import adafruit_ble
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble_ibbq import IBBQService

import hbmqtt

# PyLint can't find BLERadio for some reason so special case it here.
ble = adafruit_ble.BLERadio()  # pylint: disable=no-member

ibbq_connection = None
NoneType = type(None)

mqclient = hbmqtt.hbclient()
mqclient.connect()
mqttfmt = 'device/bbq/sensor/%d/temperature/announce'

saved_temps = [0,0,0,0,0,0]
last_data = [0.0,0.0,0.0,0.0,0.0,0.0]

while True:
    print("Scanning...")
    for adv in ble.start_scan(ProvideServicesAdvertisement, timeout=5):
        if IBBQService in adv.services:
            print("found an IBBq advertisement")
            while True:
                try:
                    ibbq_connection = ble.connect(adv)
                    print("Connected")
                    break
                except:
                    #print(sys.exc_info())
                    print('Trying to connect')
            break

    # Stop scanning whether or not we are connected.
    ble.stop_scan()

    if ibbq_connection and ibbq_connection.connected:
        ibbq_service = ibbq_connection[IBBQService]
        ibbq_service.init()
        try:
            temps = ibbq_service.temperatures
            #print('read 1st')
        except:
            pass
            #print('failed 1st')
        while ibbq_connection.connected:
            temps = ibbq_service.temperatures
            if temps != None:
                etemp = enumerate(temps)
                #print('etemp',etemp)
                for probe in etemp:
                    #print('probe',probe)
                    temp_f = 32 + (probe[1]*9/5)
                    if temp_f > 2000:
                        continue
                    n = probe[0]
                    now = time.monotonic()
                    since_data = now - last_data[n]
                    print(since_data)
                    if temp_f != saved_temps[n] or since_data > 300:
                        saved_temps[n] = temp_f
                        last_data[n] = now
                        print ('Probe %d: %f'%(n,temp_f))
                        topic = mqttfmt%(n)
                        print('topic',topic)
                        try:
                            mqclient.connect()
                            #mqclient.publish( topic ,temp_f)
                            mqclient.signal( topic ,temp_f)
                        except:
                            mqclient.logerror('mqtt failed')

            time.sleep(2)
