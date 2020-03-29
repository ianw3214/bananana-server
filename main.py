#!/usr/bin/env python

import asyncio
import websockets
import os
import json

# TEMPORARY
import datetime
import random

CONNECTED = set()
CLIENTS = []

async def sendMessage(message):
    for socket in CONNECTED:
        await socket.send(message)

async def consumer(message):
    # ASSUME INCOMING MESSAGE IS A JSON OBJECT
    command = json.loads(message)
    print(command)
    if command["command"] == "create":
        CLIENTS.append({"id": command["id"]})
        sendMessage({"command":"create", "id":command["id"], "x":0, "y":0})
    print(CLIENTS)

async def producer():
    pass    

async def consumer_handler(websocket, path):
    async for message in websocket:
        await consumer(message)

async def producer_handler(websocket, path):
    pass
    # while True:
    #     message = await producer()
    #     await websocket.send(message)
        # SEND MESSAGES AT A 1 SECOND INTERVAL
        # await asyncio.sleep(1)

# WebSocket server example
async def hello(websocket, path):
    # ADD THE WEBSOCKET TO THE PATH FOR EASY MESSAGE BROADCASTING
    CONNECTED.add(websocket)
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
