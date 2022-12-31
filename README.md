# Pi Pico Project: Temperature and Humidity Server

This project uses:

* A Pi Pico W
* An AM2320 Temperature and Humidity Sensor
* A Pi Pico Proto Board
* 2 x 4k7 Ohm resistors
* Various small connecting wires
* A small modicum of soldering skill (from the pictures you can see... that's *very* small :-) )

To produce an HTTP (NOT HTTPS) REST Server delivering 2 GET requests returning application/json data about

* The service (`GET <ipaddr>/about`)
* The current temperature and humidity readings from the sensor (`GET <ipaddr>/measurement`)

TODO:
* Wiring
* Pictures
* Code breakdown and changes/potential resuse.
* Usage
* Links
