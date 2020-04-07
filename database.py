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
            "inventory": ["root"]
        }, name)
        document = users.document(name).get()
        if not document.exists:
            # TODO: HANDLE ERROR
            pass
        return document.to_dict()

def addPlayerInventoryItem(name, item):
    users = firestore.Client(credentials={
        "client_email": os.getenv("client_email"),
        "private_key": os.getenv("private_key")
    }).collection(u'users')
    document = users.document(name).get()
    if not document.exists:
        # TODO: HANDLE ERROR
        pass
    player_data = document.to_dict()
    player_data["inventory"].append(item)
    users.document(name).set(player_data)
