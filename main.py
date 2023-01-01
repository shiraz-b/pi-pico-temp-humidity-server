from machine import Pin, I2C
import am2320
import time
import restServer
import sensitiveData
import ledControl

def tempHumidityReading(sensor):
    if ( sensor.measure() ):
        temperature = sensor.temperature()
        humidity = sensor.humidity()
    else:
        # Something bad happened - return 0s
        temperature = 0
        humidity = 0
    return temperature, humidity

def main():
    # Add short delay when starting from boot to allow
    # I2C devices to settle
    time.sleep_ms(1000)

    # Setup temperature and humid sensor (part am2320)
    i2c_dev = machine.I2C(0,scl=Pin(5),sda=Pin(4),freq=400000)  # start I2C on GPIO 4&5
    sensor = am2320.AM2320(i2c_dev)
    
    # Setup the REST service and looks for GETs of /about and /measurement
    rest = restServer.RESTService(sensitiveData.SSIDDATA.ssid, sensitiveData.SSIDDATA.password)
    connected = rest.connectAndListen()
    allowed_resources = ["/about", "/measurement"]    
    
    # repeat forever
    while True:
        resource = rest.obtainRequest("GET", *allowed_resources)
        print("Got resource: " + resource)
        if resource == "/measurement":
            temp, humid = tempHumidityReading(sensor)
            response = "{ \"temperature\" : \"" + str(temp) + "\", \"temperatureUnit\" : \"celsius\", \"humidity\" : \"" + str(humid) + "\" }"
            print("Temp: {}C RH {}%".format(temp, humid))
        elif resource == "/about":
            response = "{ \"what\" : \"Temperature and Humidity Sensor\", \"who\" : \"Shiraz Billimoria\", \"when\" : \"Dec 2022\", \"where\" : \"https://github.com/shiraz-b/pi-pico-temp-humidity-server\" }"
        else:
            response = "{ \"error\" : \"how did you get here?\" }"
        ledControl.toggleLED("LED")
        rest.sendResponse(response)
        print("Waiting for REST Request")

main()
