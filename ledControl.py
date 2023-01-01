from machine import Pin
import time

# Set of functions to control LEDs

def toggleLED(led):
    Pin(led, Pin.OUT).toggle()
    
def flashLED(led, flashTime, flashRate):
    # Flash the internal LED quickly for 2 seconds to signal good connection
    for x in range(flashTime/flashRate):
        Pin(led, Pin.OUT).toggle()
        time.sleep_ms(flashRate)
    # Leave LED in an off state
    Pin(led, Pin.OUT).off()

