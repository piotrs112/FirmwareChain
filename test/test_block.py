from data_manipulation import transaction_fromJSON
from transaction import Transaction
from blockchain import Blockchain
from block import Block
from signing import sign, verify_signature, is_signed

from datetime import datetime

def test_block_creation():
    pk = Blockchain.generate_private_key()
    pub_k = Blockchain.generate_public_key(pk)
    b = Block(0, [], datetime.now(), "Hash", pub_k)
    sign(b, pk)
    assert is_signed(b) and verify_signature(b)

def test_eq():
    pk = Blockchain.generate_private_key()
    pub_k = Blockchain.generate_public_key(pk)

    t = Transaction(pub_k, {'test': 'data'})
    sign(t, pk)

    dt = datetime.now()

    b1 = Block(7, [t], dt, "0", pub_k)
    b2 = Block(7, [t], dt, "0", pub_k)

    sign(b1, pk)
    sign(b2, pk)

    assert b1 == b2

def test_hash():
    pk = Blockchain.generate_private_key()
    pub_k = Blockchain.generate_public_key(pk)

    t = Transaction(pub_k, {'test': 'data'})
    sign(t, pk)

    dt = datetime.now()

    b1 = Block(7, [t], dt, "0", pub_k)
    b2 = Block(7, [t], dt, "0", pub_k)

    sign(b1, pk)
    sign(b2, pk)

    assert b1.sha() == b2.sha()
