import asyncio
from server import Server
from transceiver import Transceiver

async def main():
    transceiver = Transceiver()
    server = Server(transceiver)

    await asyncio.gather(
        transceiver.run(),  # Runs arrow pattern updates
        server.run()  # Runs web server & WebSocket
    )

if __name__ == '__main__':
    asyncio.run(main())
