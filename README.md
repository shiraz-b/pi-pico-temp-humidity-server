# Pi Pico Project: Temperature and Humidity Server
## Introduction
This project uses a Pi Pico W and Temp/Humidity Sensor to produce an HTTP (NOT HTTPS) REST Server delivering
2 GET requests returning application/json data about:

* The service (`GET <ipaddr>/about`)
* The current temperature and humidity readings from the sensor (`GET <ipaddr>/measurement`)
## Hardware
The Hardware I used

* [A Pi Pico W](https://shop.pimoroni.com/products/raspberry-pi-pico-w)
* [An AM2320 Temperature and Humidity Sensor](https://shop.pimoroni.com/products/digital-temperature-and-humidity-sensor)
* [A Pi Pico Proto Board](https://shop.pimoroni.com/products/pico-proto)
* [2 x 4k7 Ohm resistors](https://shop.pimoroni.com/products/e3-series-resistor-set-480pcs-10e-to-1m)
* [Various Headers](https://shop.pimoroni.com/products/maker-essentials-various-headers)
* Various small connecting wires
* A small modicum of soldering skill (from the pictures you can see... that's *very* small :-) )

## Wiring

I took [this link](https://learn.adafruit.com/adafruit-am2320-temperature-humidity-i2c-sensor/python-circuitpython)
as a basis for the wiring diagram.

The web site here tells us that the Pi Pico already has pullup resistors built into the GPIOs so you don't need to
bother with them.  But, trust me, save youself about an hour and just put them in - turns out that it takes some
time for the GPIOs to come up and, by that time, the AM2320 has already set itself up in single-bus mode and we need
to have the Serial Clock (SCL) line high on initialisation for us to get into I2C mode.

TODO:
* Wiring
* Pictures
* Code breakdown and changes/potential resuse.
* Usage
* Links
