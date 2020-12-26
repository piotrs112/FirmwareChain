from random import randint
from time import sleep

import pytest
from py2p.base import Message

from blockchain import Blockchain
from node import Node
from signing import sign
from transaction import Transaction


def test_init():
    n = Node()
    assert n.sock.status == "Nominal"


def test_connection():
    port = randint(6002, 6100)
    port2 = port + 1

    n = Node(port=port)
    n2 = Node(port=port2)

    n.sock.connect("0.0.0.0", port=port2)
    sleep(0.1)

    assert n.sock.id in [peer for peer in n2.sock.routing_table]
    assert n2.sock.id in [peer for peer in n.sock.routing_table]

def test_transaction_propagation():
    port = randint(6002, 6100)
    port2 = port + 1

    server = Node(port)
    node = Node(port2)

    node.sock.connect("0.0.0.0", port=port)
    sleep(0.1)

    t = Transaction(server.bc.public_key, "v1", "hash@#$", "main.h")
    sign(t, server.bc.private_key)
    server.bc.add_transaction(t)

    sleep(0.1)
    assert node.bc.pending_transactions[0] == t

def test_mining():
    port = randint(6002, 6100)
    port2 = port + 1

    server = Node(port)
    node = Node(port2)
    offline = Blockchain()

    node.sock.connect("0.0.0.0", port=port)
    sleep(0.1)

    t = Transaction(server.bc.public_key, "v1", "hash@#$", "main.h")
    sign(t, server.bc.private_key)
    server.bc.add_transaction(t)

    sleep(0.1)

    server.sock.send(type="mine")
    offline.add_transaction(t)
    offline.mine()
    #todo 
   