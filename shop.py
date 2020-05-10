import database
import players

# Shop items are hard coded for now
# TODO: eventually will want to read from a file
def buy(command):
    item = command["item"]
    # Handle the hairs
    if item == 0 or item == 1:
        wardrobe = database.getPlayerWardrobeData(command["name"])
        if item not in wardrobe["hair"]["unlocked"]:
            # Also need to check that the player has enough money
            player = database.getPlayerData(command["name"])
            if item == 0 and player["money"] >= 50:
                player["money"] = player["money"] - 50
                wardrobe["hair"]["unlocked"] += [0]
                database.setPlayerWardrobeData(command["name"], wardrobe)
                database.setPlayerData(command["name"], player)
                players.sendMoneyInfo(command)
                # Also send the wardrobe info so we can update it on client side
                players.sendWardrobeInfo({"name": command["name"], "id": command["id"]})
            elif item == 1 and player["money"] >= 100:
                player["money"] = player["money"] - 100
                wardrobe["hair"]["unlocked"] += [1]
                database.setPlayerWardrobeData(command["name"], wardrobe)
                database.setPlayerData(command["name"], player)
                players.sendMoneyInfo(command)
                # Also send the wardrobe info so we can update it on client side
                players.sendWardrobeInfo({"name": command["name"], "id": command["id"]})
