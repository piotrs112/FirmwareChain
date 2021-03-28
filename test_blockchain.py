from datetime import datetime
from node import Node
from time import sleep

from block import Block
from blockchain import Blockchain
from signing import numerize_public_key, sign
from transaction import Transaction


def test_init():
    bc = Blockchain()
    assert len(bc.chain) == 1
    assert bc.pending_transactions == []
    assert Block(0, [], datetime(2000, 1, 1, 0, 0), "0", None) == bc.last_block
    assert bc.sock == None


def test_add_transaction():
    bc = Blockchain()
    t = Transaction(bc.public_key, "v1", "xyz", "main.h")
    sign(t, bc.private_key)

    bc.add_transaction(t)
    assert t in bc.pending_transactions
    assert bc.pending_transactions[0].toJSON() == t.toJSON()

def test_mining():
    bc = Blockchain()
    t = Transaction(bc.public_key, "v1", "xyz", "main.h")
    sign(t, bc.private_key)

    bc.add_transaction(t)
    bc.mine()

    assert bc.verify_chain()
    assert bc.last_block.transactions[0] == t

def test_poah():
    b1 = Blockchain()
    b2 = Blockchain()
    b3 = Blockchain()

    nodes = {
        "1": 10,
        "3": 10,
        "5": 0,
    }

    b1.nodes = nodes
    b2.nodes = nodes
    b3.nodes = nodes

    assert b1.proof_of_authentication() == b2.proof_of_authentication() == b3.proof_of_authentication(), "Different chosen leaders"

    leader1 = b1.proof_of_authentication()
    sleep(1)
    leader2 = b1.proof_of_authentication()
    assert leader1 is not leader2 and leader1 != "5" and leader2 != "5"

def test_add_validated():
    node = Node()
    bc = node.bc
    t = Transaction(bc.public_key, "v1", "xyz", "main.h")
    sign(t, bc.private_key)
    bc.add_transaction(t)
    bc.mine()
    assert bc.nodes[bc.sock.id.decode('utf-8')] == 10
    