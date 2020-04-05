#!/usr/bin/env python

import asyncio
import websockets
import os
import json
import sys

from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials

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

async def producer(websocket):
    players.getMessages(websocket)

async def consumer_handler(websocket, path):
    async for message in websocket:
        await consumer(message, websocket)
    # Once the while loop breaks, that means the client has disconnected
    players.removePlayer(websocket)

async def producer_handler(websocket, path):
    while True:
        message = await producer(websocket)
        if message is not None:
            await websocket.send(message)
        # SEND MESSAGES AT A 1 SECOND INTERVAL
        await asyncio.sleep(0.3)
        # JUST LEAVE UPDATE LOOP HERE AND HOPE IT WORKS
        # TODO: This is wrong, this will update the players each tick once for EVERY PLAYER
        # E.G. the more players that exist, the faster it will update
        players.updatePlayers()

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

    # cred = credentials.Certificate("bananana-e9e13-firebase-adminsdk-o1si6-9f161ccc64.json")
    # firebase_admin.initialize_app(cred)

    # Firestore stuff
    db = firestore.Client()


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

    
