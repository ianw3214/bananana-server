import os

from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials

def init():
    pass

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
