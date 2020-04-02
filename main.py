#!/usr/bin/env python

import asyncio
import websockets
import os
import json
import sys
import random

# TEMPORARY
import datetime
import random

# CLIENT PROPERTIES
# - id: client id
# - x: client x position
# - y: client y position
# - state: client state in case the client is doing something
CLIENTS = []

def getClient(target):
    for client in CLIENTS:
        if client["id"] == target:
            return client
    return None

# TEMPORARY CODE FOR FISHING
FISH = ["GOLDFISH", "COMMON CARP", "CLOWNFISH", "CATFISH", "SWORDFISH", "SALMON", "LARGE COD", "SERGIO"]

def update():
    for client in CLIENTS:
        if client["state"] == "fishing":
            # Randomly let the client find a fish
            if random.randint(0, 10) == 0:
                client["state"] = "default"
                sendMessage({
                    "command": "fish",
                    "id": client["id"],
                    "fish": FISH[random.randint(0, 7)]
                })

def sendMessage(message):
    for client in CLIENTS:
        client["messages"].append(message)

async def consumer(message, websocket):
    # ASSUME INCOMING MESSAGE IS A JSON OBJECT
    command = json.loads(message)
    if command["command"] == "create":
        # NOTIFY THE CLIENT OF EXISTING CLIENTS
        messages = []
        for client in CLIENTS:
            messages.append({"command": "create", "id": client["id"], "x": client["x"], "y": client["y"]})
        CLIENTS.append({
            "id": command["id"], 
            "x": 480,
            "y": 360,
            "socket": websocket, 
            "messages": messages,
            "state": "default"
        })
        # Have an initial message in the client to signal it has joined
        sendMessage({"command": "create", "id": command["id"], "x": 480, "y": 360, "state": "default"})
    if command["command"] == "move":
        client = getClient(command["id"])
        if client and client["state"] == "default":
            client["x"] = command["x"]
            client["y"] = command["y"]
            sendMessage({"command": "move", "id": command["id"], "x": command["x"], "y": command["y"], "debug": "STATE: " + client["state"]})
    if command["command"] == "interact":
        client = getClient(command["id"])
        if client:
            if command["action"] == "fishing":
                client["state"] = "fishing"
            sendMessage({"command": "interact", "id": command["id"], "action": "fishing"})

async def producer(websocket):
    for client in CLIENTS:
        if client["socket"] == websocket:
            if len(client["messages"]) > 0:
                message = { "messages": client["messages"].copy() }
                client["messages"].clear()
                return json.dumps(message)

async def consumer_handler(websocket, path):
    async for message in websocket:
        await consumer(message, websocket)
    # Once the while loop breaks, that means the client has disconnected
    target = 0
    for client in CLIENTS:
        if client["socket"] == websocket:
            target = client["id"]
            CLIENTS.remove(client)
    if target != 0:
        sendMessage({"command": "remove", "id": target})

async def producer_handler(websocket, path):
    while True:
        message = await producer(websocket)
        if message is not None:
            await websocket.send(message)
        # SEND MESSAGES AT A 1 SECOND INTERVAL
        await asyncio.sleep(0.5)
        # JUST LEAVE UPDATE LOOP HERE AND HOPE IT WORKS
        update()

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

if __name__ == "__main__":
    address = "0.0.0.0"
    port = 0

    if os.getenv("ADDRESS"):
        address = os.environ["ADDRESS"]
    if os.getenv("PORT"):
        port = os.environ["PORT"]

    start_server = websockets.serve(hello, address, port);
    print("SERVER STARTED")

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

    
