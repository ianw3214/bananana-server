#!/usr/bin/env python

import asyncio
import websockets
import os
import json
import sys

import database
import players

async def consumer(message, websocket):
    # ASSUME INCOMING MESSAGE IS A JSON OBJECT
    command = json.loads(message)
    if command["command"] == "create":
        players.createPlayer(command, websocket)
    if command["command"] == "move":
        players.movePlayer(command)
    if command["command"] == "interact":
        players.playerInteract(command)
    if command["command"] == "inventory":
        players.sendInventoryInfo(command)
    if command["command"] == "money":
        players.sendMoneyInfo(command)
    if command["command"] == "sell":
        players.sellInventoryItem(command)

async def producer(websocket):
    return players.getMessages(websocket)

async def consumer_handler(websocket, path):
    async for message in websocket:
        await consumer(message, websocket)
    # Once the while loop breaks, that means the cinlient has disconnected
    players.removePlayer(websocket)

async def producer_handler(websocket, path):
    while True:
        message = await producer(websocket)
        if message is not None:
            await websocket.send(message)
        # SEND MESSAGES AT A 1 SECOND INTERVAL
        await asyncio.sleep(0.2)

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

async def update_loop():
    while True:
        players.updatePlayers()
        # Update players only a few times every second
        await asyncio.sleep(0.2)

if __name__ == "__main__":
    database.getPlayerData("IAN");

    address = "0.0.0.0"
    port = 0
    if os.getenv("ADDRESS"):
        address = os.environ["ADDRESS"]
    if os.getenv("PORT"):
        port = os.environ["PORT"]

    database.init()

    start_server = websockets.serve(hello, address, port);
    
    asyncio.get_event_loop().create_task(update_loop())

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

    
