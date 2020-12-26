from datetime import datetime

from block import Block
from blockchain import Blockchain
from signing import sign
from transaction import Transaction


def test_init():
    bc = Blockchain()
    assert len(bc.chain) == 1
    assert bc.pending_transactions == []
    assert Block(0, [], datetime(2000, 1, 1, 0, 0), "0", None) in bc.chain
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

def test_poa():
    b1 = Blockchain()
    b2 = Blockchain()
    b3 = Blockchain()

    nodes = {'c': 10, 'b': 5, 'd': 15}
    b1.nodes = nodes
    b2.nodes = nodes
    b3.nodes = nodes

    assert b1.proof_of_authority() == b2.proof_of_authority() == b3.proof_of_authority()