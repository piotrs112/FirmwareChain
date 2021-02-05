from blockchain import Blockchain
from block import Block
from signing import sign, verify_signature, is_signed

from datetime import datetime

def test_block_creation():
    pk = Blockchain.generate_private_key()
    pub_k = Blockchain.generate_public_key(pk)
    b = Block("0", [], datetime.now(), "Hash", pub_k)
    sign(b, pk)
    assert is_signed(b) and verify_signature(b)

    