#!/usr/bin/env python

import asyncio
import websockets
import os
import json

# TEMPORARY
import datetime
import random

CLIENTS = []


async def consumer(message, websocket):
    # ASSUME INCOMING MESSAGE IS A JSON OBJECT
    command = json.loads(message)
    print(command)
    if command["command"] == "create":
        CLIENTS.append({"id": command["id"], "socket": websocket, "messages":[
            # Have an initial message in the client to signal it has joined
            {"command": "create", "id": command["id"], "x":0, "y":0}
        ]})
    print(CLIENTS)

async def producer(websocket):
    for client in CLIENTS:
        if client["socket"] == websocket:
            if len(client["messages"]) > 0:
                return json.dumps(client["messages"].pop(0))
            

async def consumer_handler(websocket, path):
    async for message in websocket:
        await consumer(message, websocket)

async def producer_handler(websocket, path):
    while True:
        message = await producer(websocket)
        if message is not None:
            await websocket.send(message)
        # SEND MESSAGES AT A 1 SECOND INTERVAL
        await asyncio.sleep(1)

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
