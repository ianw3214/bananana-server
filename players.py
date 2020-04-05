import random
import json

# PLAYERPROPERTIES
# - id: player id
# - x: player x position
# - y: player y position
# - state: player state in case the player is doing something
PLAYERS = []

# TEMPORARY CODE FOR FISHING
FISH = ["GOLDFISH", "COMMON CARP", "CLOWNFISH", "CATFISH",
        "SWORDFISH", "SALMON", "LARGE COD", "SERGIO"]

def sendMessage(message):
    for player in PLAYERS:
        player["message"].append(message)

def getPlayer(target):
    for player in PLAYERS:
        if player["id"] == target:
            return player
    return None

def updatePlayers():
    for player in PLAYERS:
        if player["state"] == "fishing":
            # Randomly let the player find a fish
            if random.randint(0, 10) == 0:
                player["state"] == "default"
                sendMessage({
                    "command": "fish",
                    "id": player["id"],
                    "fish": FISH[random.randint(0, 7)]
                })

def createPlayer(data, websocket):
    # Notify the client of existing clients
    messages = []
    for player in PLAYERS:
        messages.append({
            "command": "create",
            "id": player["id"],
            "name": player["name"],
            "x": player["x"],
            "y": player["y"],
            "state": player["state"]
        })
    # Add the player to our list of players
    PLAYERS.append({
        "id": data["id"],
        "name": data["name"],
        "x": 480,
        "y": 360,
        "socket": websocket,
        "messages": messages,
        "state": "default"
    })
    # Notify all clients of the new player
    sendMessage({
        "command": "create",
        "id": data["id"],
        "name": data["name"],
        "x": 480,
        "y": 360,
        "state": "default"
    })

def movePlayer(data):
    player = getPlayer(data["id"])
    if player and player["state"] == "default":
        player["x"] = data["x"]
        player["y"] = data["y"]
        sendMessage({
            "command": "move",
            "id": data["id"],
            "x": data["x"],
            "y": data["y"],
            "debug": "State: " + player["state"]
        })

def playerInteract(data):
    player = getPlayer(data["id"])
    if player:
        if data["cation"] == "fishing":
            player["state"] = "fishing"
        sendMessage({
            "command": "interact",
            "id": data["id"],
            "action": "fishing"
        })

def getMessages(websocket):
    for player in PLAYERS:
        if player["socket"] == websocket:
            if len(player["messages"]) > 0:
                message = {"messages": player["messages"].copy()}
                player["messages"].clear()
                return json.dumps(message)

def removePlayer(websocket):
    target = 0
    for player in PLAYERS:
        if player["socket"] == websocket:
            target = player["id"]
            PLAYERS.remove(player)
    if target != 0:
        sendMessage({"command": "remove", "id": target})