# Pi Pico Project: Temperature and Humidity Server
## Introduction
This project uses a Pi Pico W and Temp/Humidity Sensor to produce an HTTP (NOT HTTPS) REST Server delivering
2 GET requests returning application/json data about:

* The service (`GET <ipaddr>/about`)
* The current temperature and humidity readings from the sensor (`GET <ipaddr>/measurement`)

Please note, this is a fairly naive implementation of both Hardware and Software.  I've been using this as a learning exercise.
Specifically I want to produce a few of these units, stick them around the house and connect them to my
[Home Assistant](https://www.home-assistant.io/) Pi 3 Server to get data on how the house heats up/cools down during the day.

I'm very happy to hear from anybody if they have any tips/things I'm missed/things I've just got wrong!

**NOTE** The code here is incomplete.  **You need to add your access point SSID and password into `sensitiveData.py`**.
## Hardware
The Hardware I used

* [A Pi Pico W](https://shop.pimoroni.com/products/raspberry-pi-pico-w)
* [An AM2320 Temperature and Humidity Sensor](https://shop.pimoroni.com/products/digital-temperature-and-humidity-sensor)
* [A Pi Pico Proto Board](https://shop.pimoroni.com/products/pico-proto)
* [2 x 4k7 Ohm resistors](https://shop.pimoroni.com/products/e3-series-resistor-set-480pcs-10e-to-1m)
* [Various Headers](https://shop.pimoroni.com/products/maker-essentials-various-headers)
* Various small connecting wires
* A small modicum of soldering skill (from the pictures you can see... that's *very* small :-) )

Total Cost: ~£10

Energy: ~200mW.  I've seen a spike to around 255mW.  At 33p/kWh thats around 57p per year to keep this on constantly!
## Wiring

I took [this link](https://learn.adafruit.com/adafruit-am2320-temperature-humidity-i2c-sensor/python-circuitpython)
as a basis for the wiring diagram.

The web site here tells us that the Pi Pico already has pullup resistors built into the GPIOs so you don't need to
bother with them.  But, trust me, save youself about an hour and just put them in - turns out that it takes some
time for the GPIOs to come up and, by that time, the AM2320 has already set itself up in single-bus mode and we need
to have the Serial Clock (SCL) line high on initialisation for us to get into I2C mode.

Thought: Maybe you don't need the pullup resistor for the Serial Data (SDA) line.  If I've got a moment I might
change my breadboard layout and let you know.  This would save one resistor.

![Front](https://github.com/shiraz-b/pi-pico-temp-humidity-server/blob/main/PXL_20221231_132143934.jpg "Front")
![Back](https://github.com/shiraz-b/pi-pico-temp-humidity-server/blob/main/PXL_20221231_132149784.jpg "Back showing my poor soldering!")

NOTES:  The wiring is quite simple:
* RED: +3v to +3v.  Power to the AM2320.
* BLACK: Serial Data (SDA).  Goes to GPIO 4 for the I2C SDA.  Also connected to +3v via a 4k7 Ohm Resistor.
* BROWN: Groud to Ground.  I've put this to the ground near the +3v on the Pi PICO, but can go to any ground.
* WHITE: Serial Clock (SCL).  Goes to GPIO 5 for the I2C SCL.  Also connected to +3v via a 4k7 Ohm Resistor.

## Code breakdown and changes/potential reuse
As I said earlier, this is a fairly naive bit of work that I did during my Christmas 2022 holiday.  I'm sure this is especially
true of the software.  I have a lot of coding experience but mainly in C/C++/Java.  I'm new to Python so I'm sure this could all
be done better.

More specifically I've created Classes for Network/REST setup and LED Handling.  Not because I need it for this project
but because a) it's just good abstraction and defines well understood APIs and b) I'll be expanding and wanting to use
these modules in other projects in the future.

Some notes on the code:
* `restServer.py`

  This is a badly named module but roughly deals with the wifi setup and the binding/listening for REST calls from port 80.
Lots of scope for getting this more robust:
  * Exception Handling - this is true of *all* of this code
  * More/Better REST parsing:  Maybe a list of verbs?
  * Async: This is the biggie.  The code is synchronous at the moment a massive improvement would be to get this async.
* `am2320.py`

  This is a straight copy from [mcausers repo](https://github.com/mcauser/micropython-am2320) (many thanks!) with a minor tweak
* `ledControl.py`

  A simple class to control LEDs.  This is just a start.  I'll be adding to this module in the future.
* `main.py`

  This put's it all together.  Hardware and Network setup then a simple loop waiting for acceptable REST Input and then
  setting up and sending the relevant response.  This is crying out for better exception handling. Especially since this
  is effectively an embedded system.
  For this to work, `sensitiveData.py` needs to be altered with the SSID and password for your Access Point.
* `sensitiveData.py`

  **You need to add your access point SSID and password into `sensitiveData.py`**
  
## Usage
## Links
## Future Enhancements
* Move to MTTQ push notifications
* Investigate low power modes.  If we move to MTTQ then we should be able to:
  * Wake
  * Read temp and Humidity
  * Send reading to Home Assistant
  * Sleep
