# bbq
BBQ temperature monitoring system

## Background
I use a Nutrichef EasyBBQ PWIRBBQ80 6 channel thermometer to monitor the meat and smoker temperatures in my Big Green Egg.  The EasyBBQ phone app is disappointing in that it forgets any logged readings when the Bluetooth link is lost.  You can reconnect Bluetooth but the graph view has no previous data.  This makes it difficult to recognize when meats enter the "stall".

I have a network of smart devices throughout my house.  I've developed it myself as one of my retirement hobbies.  There are several Raspberry Pi computers running code I've written in Python.  Communications between computers and smart devices is by MQTT.  This bbq system was easily developed on top of my smart house infrastructure.

## Hardware
Following is the hardware I use.
### Thermometer
Nutrichef EasyBBQ PWIRBBQ80 6 channel thermometer.  It supports the iBBQ protocol so I can communicate with it using the adafruit_ble_ibbq library.
### Raspberry Pi Zero W
My smoker is located on a patio on the lower level of my house, one floor below the main living space.  The RPi is located inside the lower level near the patio.
### Raspberry Pi 4
The computer runs most of my smart house programs.  This is also my MySQL host.
### Raspberry Pi 3
I use a seperate RPi as my MQTT server.
### Network Attached Storage
I have a ASUSTOR disk connected to my network.  I keep the MySQL database here.
## Programs
### bbq.py
Runs on the RPi 0 near the smoker and thermometer.  Receives temperture readings and rebroadcasts them to the network as MQTT messages.  Duplicate readings are suppressed unless 5 minutes have transpired since the last message.
### bbqdb.py
Subscribes to MQTT temprature messages and saves them as records in a MySQL database.  Each record includes an index, timestamp, probe number and temperature reading.
### bbqplot.py
Reads recent records from the database (currently within the last 5 days) and uses Matplotlib to create a plot.  Creates a new plot every 5 minutes.
### bbqstates.py

Subscribes to temperature messages and maintains a state machine describing what's happening inside the smoker.  State changes are published as MQTT messages.  I also send them to my phone using the Pushbullet app.

|Meat State|Next State|Condition for Next State|Action in this State|
|----------|----------|--------|---------------------|
|Initial   |Bark     |Temp > 100|None|
|Bark      |Spritz   |Temp > 135|None|
|Spritz    |Stall    |Temp > 150, same temp repeated for 3 readings (approx 10 minutes)|Spray occasionally with ACV|
|Stall     |Wrapped  |Temp drops from stall by 25 degrees due to probe being removed to wrap meat.|Check fat render. Wrap in butcher paper|
|Wrapped   |Finishing|Temp > stall temperature|Return to smoker|
|Finishing |Done     |Temp >= 203|None|
|Done      |Cooling  |Temp < 200|Remove from smoker|
|Cooling   |Resting  |Temp < 180|None|
|Resting   |Ready    |Temp < 165|Place in cooler|
|Ready     |Reheat   |Temp < 145|Serve|
|Reheat    |Ready    |Temp > 150|Reheat in oven|

The smoker target temperture changes.  I begin at 225-250.  When all meat probes have been wrapped, the target is 250-275.  I need to add hysteresis at the boundaries.

|Smoker State|Smoker Condition|Action in this State|
|----------|----------|---------------------|
|Cold   |Temp < Low Target - 25|Monitor Closely|
|Below Target      |Temp < Low Target|Adjust vents|
|At Target     |Temp >  Low Target and < High Target|None|
|Above Target      |Temp >  High Target|Adjust vents|
|Hot      |Temp >  High Target + 25 |Monitor Closely|

### bbqpage.py
Creates a local webpage depicting cuyrrent temperatures and the current states of the smoker and meat cuts.  I can view this on my phone, laptop or TV.
### bbqlabels.py
Labels and titles for the plot and webpage.
### hbmqtt.py
Commonly used routines for MQTT communications on my network.
