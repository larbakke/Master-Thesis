# Import necessary modules
from machine import Pin
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral
import time
import random

# Create a Bluetooth Low Energy (BLE) object
ble = bluetooth.BLE()
# Create an instance of the BLESimplePeripheral class with the BLE object
sp = BLESimplePeripheral(ble)

# Set the debounce time to 0. Used for switch debouncing
debounce_time=0

# Create a Pin object for Pin 0, configure it as an input with a pull-up resistor
i=0
def createMessage():
    global i
    i+=1
    angle = 0
    distance = 0
    if i == 1:
        angle = 25
        distance = 25
    elif i == 2:
        angle = 48
        distance = 48
    elif i == 3:
        angle = -48
        distance = 4.8
    elif i == 4:
        angle = -25
        distance = 2.5
    elif i == 5:
        i=0
        
    return f"{angle};{distance}"

def blink():
    led = machine.Pin("LED", machine.Pin.OUT)
    for i in range(3):
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.2)
    led.on()

while True:
    # Check if the pin value is 0 and if debounce time has elapsed (more than 300 milliseconds)
    if ((time.ticks_ms()-debounce_time) > 1000):
        # Check if the BLE connection is established
        if sp.is_connected():
            # Create a message string
            
            msg = createMessage()
            # Send the message via BLE
            sp.send(msg)
        # Update the debounce time    
        debounce_time=time.ticks_ms()