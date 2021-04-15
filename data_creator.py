import json
import sqlite3
from base64 import b64encode

from block import Block


def add_one(uuid: str, zones):
    _modify_one_permission(uuid, zones, "add")

def remove_one(uuid: str, zones):
    _modify_one_permission(uuid, zones, "remove")

def _modify_one_permission(uuid: str, zones, command: str) -> dict:
    """
    Add permission for one person:
    :param uuid: User UUID
    :param zone: Zone list or str
    """
    return {
        command: [{
            'uuid': uuid,
            'zone': [zones] if type(zones) == str else zones,
        }]
    }

def _modify_permission(uuids: list, zones, command: str) -> dict:
    """
    Add same zone permissions for multiple users
    """
    _dict = {command: []}
    for uuid in uuids:
        _dict[command].append({
            'uuid': uuid,
            'zone': [zones] if type(zones) == str else zones,
        })
    
    return _dict

def save_to_db(block: Block):
    with sqlite3.connect('access.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS access (id INTEGER PRIMARY KEY AUTOINCREMENT, json TEXT);")

        for _t in block.transactions:
            #data = b64encode(json.dumps(_t.data).encode()).decode()
            data = json.dumps(_t.data)
            conn.execute(f"INSERT INTO access ('json') VALUES ('{data}');")
        