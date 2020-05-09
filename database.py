import os

from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials

def init():
    pass

def tryLogin(name, password):
    logins = firestore.Client().collection(u'login')
    # The documents will just be identified by the username itself
    document = logins.document(name).get()
    if document.exists:
        return password == document.to_dict()["password"]
    else:
        # Always login successfully if creating new player
        logins.add({
            "username": name,
            "password": password
        }, name)
        return True

def getPlayerData(name):
    # Firestore stuff
    users = firestore.Client().collection(u'users')
    document = users.document(name).get()
    if document.exists:
        return document.to_dict()
    else:
        users.add({
            "name": name, 
            "inventory": ["root"],
            "money": 0
        }, name)
        document = users.document(name).get()
        if not document.exists:
            # TODO: HANDLE ERROR
            pass
        return document.to_dict()

def setPlayerData(name, data):
    users = firestore.Client().collection(u'users')
    document = users.document(name).get()
    if not document.exists:
        # TODO: HANDLE ERROR
        pass
    users.document(name).set(data)

def addPlayerInventoryItem(name, item):
    users = firestore.Client().collection(u'users')
    document = users.document(name).get()
    if not document.exists:
        # TODO: HANDLE ERROR
        pass
    player_data = document.to_dict()
    player_data["inventory"].append(item)
    users.document(name).set(player_data)

def getPlayerWardrobeData(name):
    # Firestore stuff
    wardrobe = firestore.Client().collection(u'wardrobe')
    document = wardrobe.document(name).get()
    if document.exists:
        return document.to_dict()
    else:
        wardrobe.add({
            "hair": {
                "current": -1,
                "unlocked": [
                    -1
                ]
            }
        }, name)
        document = wardrobe.document(name).get()
        if not document.exists:
            # TODO: HANDLE ERROR
            pass
        return document.to_dict()

def setPlayerWardrobeData(name, data):
    wardrobe = firestore.Client().collection(u'wardrobe')
    document = wardrobe.document(name).get()
    if not document.exists:
        # TODO: HANDLE ERROR
        pass
    wardrobe.document(name).set(data)
