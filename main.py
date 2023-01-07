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
    forever = True

    # Setup temperature and humid sensor (part am2320)
    i2c_dev = machine.I2C(0,scl=Pin(5),sda=Pin(4),freq=100000)  # start I2C on GPIO 4&5
    sensor = am2320.AM2320(i2c_dev)
    
    # Setup the REST service and looks for GETs of /about and /measurement
    rest = restServer.RESTService(sensitiveData.SSIDDATA.ssid, sensitiveData.SSIDDATA.password)
    connected = rest.connectAndListen()
    allowed_resources = ["/about", "/measurement", "/stop"]
    # Yes - I know, that's terrible and not REST compliant at all.  Shouldn't have actions.. /stop should be a DELETE to the resource
    
    try:
        # repeat forever
        while forever:
            resource = rest.obtainRequest("GET", *allowed_resources)
            print("Got resource: " + resource)
            if resource == "/measurement":
                goodReading, temp, humid = tempHumidityReading(sensor)
                if goodReading:
                    response = "{\n  \"temperature\" : " + str(temp) + ",\n  \"temperatureUnit\" : \"celsius\",\n  \"humidity\" : " + str(humid) + "\n}\n"
                    print("Temp: {}C RH {}%".format(temp, humid))
                else:
                    rest.sendErrorResponse(503)
                    ledControl.toggleLED("LED")
                    continue
            elif resource == "/about":
                response = "{\n  \"what\" : \"Temperature and Humidity Sensor\",\n  \"who\" : \"Shiraz Billimoria\",\n  \"when\" : \"Dec 2022\",\n  \"where\" : \"https://github.com/shiraz-b/pi-pico-temp-humidity-server\"\n}\n"
            elif resource == "/stop":
                response = "{\n  \"state\" : \"Service Stopping\"\n}\n"
                forever = False
            else:
                response = "{\n  \"error\" : \"how did you get here?\"\n}\n"
            ledControl.toggleLED("LED")
            rest.sendResponse(response)
            print("Waiting for REST Request")
    except Exception as err:
        print(f"Top Level Error (STOPPING): Unexpected {err=}, {type(err)=}")

    # Flash for a bit.. This also allows time for the response to get sent before we shutdown
    # the network.
    ledControl.flashLED("LED", 3000, 200)
    rest.closeDownNetwork()

main()
