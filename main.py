#!/usr/bin/env python

import asyncio
import websockets
import os

# TEMPORARY
import datetime
import random

async def consumer(message):
    print(message)

async def producer():
    now = datetime.datetime.utcnow().isoformat() + "Z"
    return now

async def consumer_handler(websocket, path):
    async for message in websocket:
        await consumer(message)

async def producer_handler(websocket, path):
    while True:
        message = await producer()
        await websocket.send(message)
        await asyncio.sleep(random.random() * 5)

# WebSocket server example
async def hello(websocket, path):
    print("HELLO FUNCTION START")
    
    consumer_task = asyncio.ensure_future(consumer_handler(websocket, path))
    producer_task = asyncio.ensure_future(producer_handler(websocket, path))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
            task.cancel()

    # while True:
    #         now = datetime.datetime.utcnow().isoformat() + "Z"
    #         await websocket.send(now)
    #         await asyncio.sleep(random.random() * 3)

start_server = websockets.serve(hello, "0.0.0.0", os.environ["PORT"])

print("SERVER STARTED")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
