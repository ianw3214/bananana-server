import database
import players

# Shop items are hard coded for now
# eventually will want to read from a file
def buy(command):
    if command["item"] == 0:
        # This is the basic hair
        wardrobe = database.getPlayerWardrobeData(command["name"])
        if 0 not in wardrobe["hair"]["unlocked"]:
            # Also need to check that the player has enough money
            player = database.getPlayerData(command["name"])
            if player["money"] >= 50:
                player["money"] = player["money"] - 50
                wardrobe["hair"]["unlocked"] += [0]
                database.setPlayerWardrobeData(command["name"], wardrobe)
                database.setPlayerData(command["name"], player)
                players.sendMoneyInfo(command)
