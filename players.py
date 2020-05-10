import random
import json

import database

# PLAYERPROPERTIES
# - id: player id
# - x: player x position
# - y: player y position
# - state: player state in case the player is doing something
PLAYERS = []
FAILED_LOGINS = {}

# TEMPORARY CODE FOR FISHING
FISH = ["GOLDFISH", "COMMON CARP", "CLOWNFISH", "CATFISH",
        "SWORDFISH", "SALMON", "LARGE COD", "SERGIO"]

def sendMessage(message):
    for player in PLAYERS:
        player["messages"].append(message)

def sendMessageTo(message, id):
    for player in PLAYERS:
        if player["id"] == id:
            player["messages"].append(message)
            break

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
                fish = FISH[random.randint(0, 7)]
                player["state"] = "default"
                sendMessageTo({
                    "command": "fish",
                    "id": player["id"],
                    "fish": fish,
                    "debug": "Name: " + player["name"]
                }, player["id"])
                database.addPlayerInventoryItem(player["name"], fish)
                # Also send inventory info once the player fishes a new fish
                sendInventoryInfo({"name": player["name"], "id": player["id"]})

def login(data, websocket):
    # Make sure the player exists in the database
    result = database.tryLogin(data["name"], data["password"])
    if result == database.LoginResult.SUCCESS:
        # Create a new session ID for the player
        session_id = random.randint(0, 1000000)
        createPlayer(data["name"], session_id, websocket)
        sendMessageTo({
            "command": "login",
            "success": True,
            "id": session_id
        }, session_id)
        database.Login(data["name"], session_id)
    elif result == database.LoginResult.SESSION_EXISTS:
        FAILED_LOGINS[websocket] = database.LoginResult.SESSION_EXISTS
    else:
        FAILED_LOGINS[websocket] = database.LoginResult.WRONG_PASSWORD

def createPlayer(name, session_id, websocket):
    # Make sure the player exists in the database
    database.getPlayerData(name)
    wardrobe = database.getPlayerWardrobeData(name)
    # Notify the client of existing clients
    messages = []
    for player in PLAYERS:
        messages.append({
            "command": "create",
            "id": player["id"],
            "name": player["name"],
            "x": player["x"],
            "y": player["y"],
            "state": player["state"],
            "hair": player["hair"]
        })
    # Add the player to our list of players
    PLAYERS.append({
        "id": session_id,
        "name": name,
        "x": 480,
        "y": 480,
        "socket": websocket,
        "messages": messages,
        "state": "default",
        "hair": wardrobe["hair"]["current"]
    })
    # Notify all clients of the new player
    sendMessage({
        "command": "create",
        # TODO: THIS ID SHOULD REALLY NOT BE BROADCASTED TO ALL PLAYERS
        "id": session_id,
        "name": name,
        "x": 480,
        "y": 480,
        "state": "default",
        "hair": wardrobe["hair"]["current"],
        "debug": database.getPlayerData("default")["name"]
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
        if data["action"] == "fishing":
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
    return None

def removePlayer(websocket):
    target = 0
    for player in PLAYERS:
        if player["socket"] == websocket:
            database.Logout(player["name"])
            target = player["id"]
            PLAYERS.remove(player)
    if target != 0:
        sendMessage({"command": "remove", "id": target})


def sendInventoryInfo(command):
    player_db = database.getPlayerData(command["name"])
    sendMessageTo({
        "command": "inventory",
        "inventory": player_db["inventory"]
    }, command["id"])

def sendWardrobeInfo(command):
    wardrobe = database.getPlayerWardrobeData(command["name"])
    sendMessageTo({
        "command": "wardrobe",
        "wardrobe": wardrobe
    }, command["id"])

def sendMoneyInfo(command):
    # GET THE NAME FROM COMMAND ID
    target = None
    for player in PLAYERS:
        if (player["id"] == command["id"]):
            target = player
    if not target:
        return
    player_db = database.getPlayerData(target["name"])
    sendMessageTo({
        "command": "money",
        "money": player_db["money"]
    }, command["id"])

def sellInventoryItem(command):
    # GET THE NAME FROM COMMAND ID
    target = None
    for player in PLAYERS:
        if (player["id"] == command["id"]):
            target = player
    if not target:
        return
    player_db = database.getPlayerData(target["name"])
    # The incoming index doesn't account for the root, so we need to account for that
    fish = player_db["inventory"][command["index"]]
    if fish == "SERGIO":
        player_db["money"] = player_db["money"] + 10
    else:
        player_db["money"] = player_db["money"] + 1
    del player_db["inventory"][command["index"]]
    # Update the database
    database.setPlayerData(command["name"], player_db)
    # REFRESH THE INVENTORY/MONEY INFO FOR THE PLAYER ONCE UPDATED
    sendMessageTo({
        "command": "inventory",
        "inventory": player_db["inventory"]
    }, command["id"])
    sendMessageTo({
        "command": "money",
        "money": player_db["money"]
    }, command["id"])

# Items are hard coded for now
# Eventually will want to read from a file
def updatePlayerStyle(command):
    # Handle hair
    item = command["item"]
    if item == -1 or item == 0 or item == 1:
        wardrobe = database.getPlayerWardrobeData(command["name"])
        # Make sure it is unlocked to be able to equip it
        if item in wardrobe["hair"]["unlocked"]:
            wardrobe["hair"]["current"] = item
            database.setPlayerWardrobeData(command["name"], wardrobe)
            sendMessage({
                "command": "style",
                "id": command["id"],
                "item": item
            })
