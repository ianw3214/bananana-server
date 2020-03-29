#!/usr/bin/env python

import asyncio
import websockets
import os
import json

# TEMPORARY
import datetime
import random

CLIENTS = []

async def consumer(message):
    # ASSUME INCOMING MESSAGE IS A JSON OBJECT
    command = json.loads(message)
    print(command)
    if command["command"] == "create":
        CLIENTS.append({"id": command["id"]})
    print(CLIENTS)

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
    consumer_task = asyncio.ensure_future(consumer_handler(websocket, path))
    producer_task = asyncio.ensure_future(producer_handler(websocket, path))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
            task.cancel()

start_server = websockets.serve(hello, "0.0.0.0", os.environ["PORT"])

print("SERVER STARTED")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
