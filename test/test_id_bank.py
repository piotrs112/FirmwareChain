import pytest
from cryptography.hazmat.backends.openssl.rsa import _RSAPublicKey

from blockchain import Blockchain
from id_bank import ID_bank
from signing import directly_numerize_public_key


@pytest.fixture
def id_bank() -> ID_bank:
    """
    ID bank setup for tests
    """
    return ID_bank(owner="pytest")

@pytest.fixture
def pub_key() -> _RSAPublicKey:
    """
    Public key setup for tests
    """
    pk = Blockchain.generate_private_key()
    return Blockchain.generate_public_key(pk)

def test_init_remove(id_bank: ID_bank):
    assert id_bank.bank == dict()
    id_bank.remove_bank()
    assert dict(id_bank.collection.find({'owner': 'pytest'})) == {}


def test_update(id_bank: ID_bank, pub_key):
    data = {
            directly_numerize_public_key(pub_key): {
            "mesh_id": "89d7s8gsd89g7d",
            "score": 10
            }
        }
    id_bank.update(data)
    assert id_bank.bank.get(directly_numerize_public_key(pub_key)) is not None

    data2 = {
            directly_numerize_public_key(pub_key): {
            "mesh_id": "89d7swerd89g7d",
            "score": 7
            }
        }
    id_bank.update(data2)
    assert id_bank.bank.get(directly_numerize_public_key(pub_key)) == data2.get(directly_numerize_public_key(pub_key))
    assert id_bank.bank.get(directly_numerize_public_key(pub_key)) != data.get(directly_numerize_public_key(pub_key))

    id_bank.remove_bank()

def test_get(id_bank: ID_bank, pub_key: _RSAPublicKey):
    id_bank.update({
        directly_numerize_public_key(pub_key): {
            "mesh_id": "meshid",
            "score": 10
            }
    })
    assert id_bank.get(pub_key) is not None, "Get function did not work"

    id_bank.remove_bank()

def test_modify(id_bank: ID_bank, pub_key: _RSAPublicKey):

    data = {
        directly_numerize_public_key(pub_key): {
        "mesh_id": "23jh54gyer",
        "score": 10
        }
    }

    id_bank.update(data)

    id_bank.modify(pub_key, -5)
    assert id_bank.get(pub_key)['score'] == 5, "Wrong score"

    id_bank.modify(pub_key, -15)
    assert id_bank.get(pub_key)['score'] == 0, "Score lower than 0"

    id_bank.modify(pub_key, 45)
    assert id_bank.get(pub_key)['score'] == 20, "Score higher than 20"

    id_bank.remove_bank()