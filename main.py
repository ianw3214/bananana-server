#!/usr/bin/env python

import asyncio
import websockets

# WebSocket server example
async def hello(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f"> greeting")

start_server = websockets.serve(hello, "localhost", 8765);

asynchio.get_event_loop().run_until_complete(start_server)
asynchio.get_event_loop().run_forever()