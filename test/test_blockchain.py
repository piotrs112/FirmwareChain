import itertools
from datetime import datetime
from random import randint
from time import sleep

from block import Block
from blockchain import Blockchain
from node import Node
from signing import sign
from transaction import Transaction


def test_init():
    bc = Blockchain()
    assert len(bc.chain) == 1
    assert bc.pending_transactions == []
    assert Block(0, [], datetime(2000, 1, 1, 0, 0), "0", None) == bc.last_block
    assert bc.sock == None


def test_add_transaction():
    bc = Blockchain()
    t = Transaction(bc.public_key, {'test': 'data'})
    sign(t, bc.private_key)

    bc.add_transaction(t)
    assert t in bc.pending_transactions
    assert bc.pending_transactions[0].toJSON() == t.toJSON()


def test_verify_chain():
    bc = Blockchain()
    b = Block(1, [], datetime.now(), hex(bc.last_block.sha()), bc.public_key)
    sign(b, bc.private_key)
    bc.chain.append(b)

    assert bc.verify_chain()


def test_mining():
    bc = Blockchain()
    t = Transaction(bc.public_key, {'test': 'data'})
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
        "1": 15,
        "3": 15,
        "5": 0,
    }

    b1.nodes = nodes
    b2.nodes = nodes
    b3.nodes = nodes

    assert b1.proof_of_authentication() == b2.proof_of_authentication(
    ) == b3.proof_of_authentication(), "Different chosen leaders"

    leader1 = b1.proof_of_authentication()
    sleep(1.1)
    leader2 = b1.proof_of_authentication()
    assert leader1 is not leader2 and leader1 != "5" and leader2 != "5"


def test_add_validated():
    node = Node()
    bc = node.bc
    t = Transaction(bc.public_key, {'test': 'data'})
    sign(t, bc.private_key)
    bc.add_transaction(t)
    bc.mine()
    assert bc.nodes[bc.sock.id.decode(
        'utf-8')] == 10 or bc.nodes[bc.sock.id.decode('utf-8')] == 15


def test_points():
    r = randint(0, 10)
    n1 = Node(port=8888-r)
    n2 = Node(port=8889-r)
    n3 = Node(port=8890-r)

    n1.sock.connect("0.0.0.0", port=8889-r)
    n1.sock.connect("0.0.0.0", port=8890-r)
    sleep(0.1)

    n1.passport()
    n2.passport()
    n3.passport()
    sleep(0.1)

    for i in range(5):
        t = Transaction(n1.bc.public_key, {'test': 'data'})
        sign(t, n1.bc.private_key)
        n1.bc.add_transaction(t)
        sleep(0.5)
        n1.sock.send('mine')
        sleep(1)

    sleep(1)
    for n in [n1, n2, n3]:
        assert len(n.bc.chain) == 6
    for n_1, n_2 in itertools.combinations([n1, n2, n3], 2):
        assert n_1.bc.chain == n_2.bc.chain
