import uasyncio as asyncio
import server
from counter import Counter


async def increment_counter(counter):
    while True:
        counter.increment()
        await asyncio.sleep(1)

async def main():
    ssid = 'Lars sin iPhone'
    password = 'Pudder123'
    counter = Counter() 
    # Run both tasks in parallel
    await asyncio.gather(
        server.start_server(ssid, password, counter),
        increment_counter(counter)
    )

# Start the async loop
asyncio.run(main())
