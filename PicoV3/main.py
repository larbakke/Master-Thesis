import bluetooth
import random
import struct
import asyncio
import aioble
from micropython import const

# Define service and characteristic UUIDs
SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
CHAR_UUID = bluetooth.UUID("abcdef01-1234-5678-1234-56789abcdef0")

# Define BLE service
service = aioble.Service(SERVICE_UUID)
char = aioble.Characteristic(service, CHAR_UUID, read=True, notify=True)

# Register the service
aioble.register_services(service)

async def send_random_data():
    while True:
        # Generate random values
        direction = random.choice([-48, -25, 0, 25, 48])  # Random direction from set values
        distance = random.uniform(0, 100)  # Random distance between 0 and 100

        # Pack data as two 4-byte floats
        data = struct.pack("ff", direction, distance)

        print(f"Sending -> Direction: {direction}, Distance: {distance}")

        # Notify any connected device
        await char.notify(data)

        # Wait for a random time between 1 to 5 seconds
        await asyncio.sleep(random.uniform(1, 5))

async def main():
    # Start BLE advertising
    print("Advertising Bluetooth device...")
    await aioble.advertise(
        5000,  # Advertise every 5 seconds
        name="Pico-BLE",
        services=[SERVICE_UUID],
    )

    # Run the send loop
    await send_random_data()

# Run the event loop
asyncio.run(main())
