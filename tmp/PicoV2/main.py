import asyncio
from server import Server
from transceiver import Transceiver

async def runTransceiver(trancseiver):
    while True:
        transceiver.update()  # Refresh the LED strip
        await asyncio.sleep(0.5)  # Wait for 0.01 seconds


async def main():
    transceiver = Transceiver()
    server = Server(transceiver)
    
    print('running a')
    await asyncio.gather(
        runTransceiver(transceiver),  # Runs arrow pattern updates
        server.run()  # Runs web server & WebSocket
    )

if __name__ == '__main__':
    asyncio.run(main())
