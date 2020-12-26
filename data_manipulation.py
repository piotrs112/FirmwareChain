import json
from datetime import datetime

import requests

from block import Block
from signing import denumerize_public_key
from transaction import Transaction


def fromJSON(block_json: str) -> Block:
    """
    Returns Block object from json data
    :param block_json: Block JSON string
    """
    block = json.loads(block_json)
    block["datetime"] = datetime.fromtimestamp(block["datetime"])
    block['block_id'] = int(block['block_id'])


    transactions = []
    for t in block["transactions"]:
        transactions.append(transaction_fromJSON(t))

    block['transactions'] = transactions
    if block['pub_key'] == None:
        pub_key = None
    else:
        pub_key = denumerize_public_key(block['pub_key'])

    result_block = Block(
        block["block_id"],
        block["transactions"],
        block["datetime"],
        block["prev_hash"],
        pub_key 
    )
    if block['signature'] is not None:
        result_block.signature = b''.fromhex(block['signature'])
    else:
        result_block.signature = None

    return result_block


def transaction_fromJSON(t: str) -> Transaction:
    """
    Returns transaction from JSON data
    :param t: Transaction JSON string
    """
    t = json.loads(t)
    pub_key = denumerize_public_key(t['public_key'])
    new_transaction = Transaction(
        pub_key, t['version'], t['file_hash'], t['filename'])
    if t['signature'] is not None:
        new_transaction.signature = b''.fromhex(t['signature'])
    return new_transaction


def get_chain(ip: str) -> list:
    """
    Gets chain from blockchain node at ip address
    :param ip: IP address
    """
    data = {'action': 'get_chain'}
    r = requests.post(f'http://{ip}/rest/', json=data)

    data = r.json()
    chain = [fromJSON(b) for b in data]

    return chain
