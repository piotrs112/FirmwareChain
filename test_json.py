import json
import requests
from datetime import datetime
from block import Block
from transaction import Transaction


def fromJSON(block_json):
    """
    Returns Block object from json data
    """
    block = json.loads(block_json)
    block["datetime"] = datetime.fromtimestamp(block["datetime"])
    block['block_id'] = int(block['block_id'])
    block['nonce'] = int(block['nonce'])

    transactions = []
    for t in block["transactions"]:
        t = json.loads(t)
        new_transaction = Transaction(None, int(t['version']), t['file_hash'], t['filename'])
        transactions.append(new_transaction)
    
    block['transactions'] = transactions
    result_block = Block(
                block["block_id"],
                block["transactions"],
                block["datetime"],
                block["prev_hash"]
                )
    result_block.nonce = block["nonce"]

    return result_block


def get_chain(ip):
    """
    Gets chain from blockchain node at ip address
    """
    data = {'action':'get_chain'}
    r = requests.post(f'http://{ip}/rest/', json=data)

    data = r.json()
    chain = [fromJSON(b) for b in data]

    return chain
