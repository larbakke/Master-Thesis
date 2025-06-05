import serial
import time
import RPi.GPIO as GPIO


class LoRa:
    def __init__(self):
        # UART setup for LoRa (using /dev/serial0)
        self.i=0
        #self.initialize_lora()

    def create_message(self):
        self.i += 1
        angle = 0
        distance = -1
        if self.i == 1:
            angle = 25
            distance = 25
        elif self.i == 2:
            angle = 48
            distance = 48
        elif self.i == 3:
            angle = -48
            distance = 4.8
        elif self.i == 4:
            angle = -25
            distance = 2.5
        elif self.i == 5:
            self.i = 0

        return f"Angle:{angle};Distance:{distance}"

    def send_command(self, command):
        if isinstance(command, str):
            command = command.encode('ascii')
        self.uart.write(command + b"\r\n")
        time.sleep(0.05)
        response = self.uart.read_all()
        if response:
            print("Response:", response.decode('utf-8', 'ignore'))

    def initialize_lora(self):
        self.uart = serial.Serial("/dev/serial0", baudrate=115200, timeout=1)
        self.send_command("AT")
        self.send_command("AT+ADDRESS=1")
        self.send_command("AT+NETWORKID=5")
        self.send_command("AT+BAND=915000000")

    def send_message(self, message):
        #message = self.create_message()
        command = f"AT+SEND=2,{len(message)},{message}"
        self.send_command(command)
        print(message)

# ---- Main program ----

#lora = LoRa()
#while True:
#    lora.send_message()
 #   time.sleep(1)
