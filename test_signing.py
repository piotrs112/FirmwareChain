import pytest

from blockchain import Blockchain
from signing import *
from transaction import Transaction


def test_denumerize_public_key():
    priv = Blockchain.generate_private_key()
    pub = Blockchain.generate_public_key(priv)
    t = Transaction(pub, '1', '2', '2')
    pub2 = numerize_public_key(t)
    pub2 = denumerize_public_key(pub2)

    assert pub.public_numbers() == pub2.public_numbers()
