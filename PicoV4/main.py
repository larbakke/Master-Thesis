import machine
import utime
from machine import Pin
import bluetooth
from ble_simple_peripheral import BLESimplePeripheral
import uasyncio as asyncio

class CommunicationController:
    def __init__(self):
        self.distance = -1
        self.direction = 0
        self.uart = machine.UART(0, baudrate=115200, tx=machine.Pin(0), rx=machine.Pin(1))
        self.ble = bluetooth.BLE()
        self.sp = BLESimplePeripheral(self.ble)
        self.led = machine.Pin("LED", machine.Pin.OUT)

    async def blink(self, times=3, delay=0.2):
        for _ in range(times):
            self.led.on()
            await asyncio.sleep(delay)
            self.led.off()
            await asyncio.sleep(delay)
        self.led.on()

    def send_command(self, command):
        if isinstance(command, str):
            command = command.encode('ascii')
        self.uart.write(command + b"\r\n")

    def initialize_lora(self):
        self.send_command("AT")
        self.send_command("AT+ADDRESS=2")
        self.send_command("AT+NETWORKID=5")
        self.send_command("AT+BAND=915000000")

    async def process_lora_message(self, message):
        try:
            print(f"Raw LoRa message: {message}")
            direction = float(message.split(";")[0].split(":")[1])
            distance = float(message.split(";")[1].split(":")[1])
            self.direction = float(direction)
            self.distance = float(distance)
            print(f"Processed: Direction={self.direction}, Distance={self.distance}")
        except Exception as e:
            print(f"Error processing message: {e}")

    async def lora_task(self): 
        print("LoRa task started")
        self.initialize_lora()
        buffer = b""
        
        while True:
            if self.uart.any():
                data = self.uart.read()
                buffer += data
                if b"\r\n" in buffer:
                    lines = buffer.split(b"\r\n")
                    buffer = lines.pop()  # Keep remaining data in buffer
                    
                    for line in lines:
                        line_str = line.decode('utf-8', 'ignore').strip()
                        if line_str.startswith("+RCV="):
                            parts = line_str.split(",")
                            if len(parts) >= 3:
                                message = parts[2]
                                await self.process_lora_message(message)
            
            await asyncio.sleep(0.001)  # Short sleep to yield control

    def createMessage(self):
        return f"{self.direction};{self.distance}"

    async def ble_task(self):
        print("BLE task started")
        last_send_time = utime.ticks_ms()
        
        prevMsg = ""
        while True:
            current_time = utime.ticks_ms()
            msg = self.createMessage()
            if utime.ticks_diff(current_time, last_send_time) >= 10 and prevMsg != msg:  # Send every second
                if self.sp.is_connected():
                    self.sp.send(msg)
                    prevMsg = msg
                    await self.blink(1, 0.05)  # Single quick blink on send
                last_send_time = current_time
            
            await asyncio.sleep(0.01)  # Short sleep to yield control

    async def main(self):
        await self.blink()  # Initial blink
        await asyncio.gather(
            self.lora_task(),
            self.ble_task()
        )

# Create instance and run
com_controller = CommunicationController()

try:
    asyncio.run(com_controller.main())
except KeyboardInterrupt:
    print("Program stopped")
finally:
    asyncio.new_event_loop()