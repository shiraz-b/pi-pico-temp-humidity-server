from machine import Pin, I2C
import am2320
import time
import restServer
import sensitiveData
import ledControl

def tempHumidityReading(sensor):
    good = False
    temperature = 0
    humidity = 0
    print("Getting sensor measurement...")
    try:
        if ( sensor.measure() ):
            print("   Temp")
            temperature = sensor.temperature()
            print("   Humidity")
            humidity = sensor.humidity()
            good = True
        else:
            print("Measurement returned bad")
    except Exception as err:
        print(f"Measurement error (continuing): Unexpected {err=}, {type(err)=}")

    return good, temperature, humidity

def main():
    # Add short delay when starting from boot to allow
    # I2C devices to settle
    time.sleep_ms(1000)

    # Setup temperature and humid sensor (part am2320)
    i2c_dev = machine.I2C(0,scl=Pin(5),sda=Pin(4),freq=100000)  # start I2C on GPIO 4&5
    sensor = am2320.AM2320(i2c_dev)
    
    # Setup the REST service and looks for GETs of /about and /measurement
    rest = restServer.RESTService(sensitiveData.SSIDDATA.ssid, sensitiveData.SSIDDATA.password)
    connected = rest.connectAndListen()
    allowed_resources = ["/about", "/measurement"]    
    
    try:
        # repeat forever
        while True:
            resource = rest.obtainRequest("GET", *allowed_resources)
            print("Got resource: " + resource)
            if resource == "/measurement":
                goodReading, temp, humid = tempHumidityReading(sensor)
                if goodReading:
                    response = "{ \"temperature\" : \"" + str(temp) + "\", \"temperatureUnit\" : \"celsius\", \"humidity\" : \"" + str(humid) + "\" }"
                    print("Temp: {}C RH {}%".format(temp, humid))
                else:
                    rest.sendErrorResponse(503)
                    ledControl.toggleLED("LED")
                    continue
            elif resource == "/about":
                response = "{ \"what\" : \"Temperature and Humidity Sensor\", \"who\" : \"Shiraz Billimoria\", \"when\" : \"Dec 2022\", \"where\" : \"https://github.com/shiraz-b/pi-pico-temp-humidity-server\" }"
            else:
                response = "{ \"error\" : \"This should not ever be seen as a 404 should have been sent before now\" }"
            ledControl.toggleLED("LED")
            rest.sendResponse(response)
            print("Waiting for REST Request")
    except Exception as err:
        print(f"Top Level Error (STOPPING): Unexpected {err=}, {type(err)=}")
        rest.closeDownNetwork()
        raise       

main()
