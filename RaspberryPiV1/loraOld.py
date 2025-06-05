import serial
import time
import RPi.GPIO as GPIO

# UART setup for LoRa (using /dev/serial0)
uart = serial.Serial("/dev/serial0", baudrate=115200, timeout=1)

i = 0

def blink():
    LED_PIN = 17  # Example GPIO pin (BCM numbering)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    for _ in range(3):
        GPIO.output(LED_PIN, True)
        time.sleep(0.5)
        GPIO.output(LED_PIN, False)
        time.sleep(0.2)
    GPIO.output(LED_PIN, True)

def create_message():
    global i
    i += 1
    angle = 0
    distance = -1
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
        i = 0

    return f"Angle:{angle};Distance:{distance}"

def send_command(command):
    if isinstance(command, str):
        command = command.encode('ascii')
    uart.write(command + b"\r\n")
    time.sleep(0.05)
    response = uart.read_all()
    if response:
        print("Response:", response.decode('utf-8', 'ignore'))

def initialize_lora():
    send_command("AT")
    send_command("AT+ADDRESS=1")
    send_command("AT+NETWORKID=5")
    send_command("AT+BAND=915000000")

def send_message():
    message = create_message()
    command = f"AT+SEND=2,{len(message)},{message}"
    send_command(command)
    print(message)

# ---- Main program ----
blink()
initialize_lora()
while True:
    send_message()
    time.sleep(1)