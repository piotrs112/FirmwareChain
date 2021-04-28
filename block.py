import hashlib
import json
from datetime import datetime
import time
from typing import List, Union

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from merklelib import MerkleTree

from signing import numerize_public_key, verify_signature
from transaction import Transaction


class Block:
    """
    Block class.
    """

    def __init__(self, block_id: int, transactions: List[Transaction], datetime: datetime, prev_hash: str, public_key: Union[RSAPublicKey, None]):
        """
        Block class constructor
        :param block_id: ID of the block, unique
        :param transactions: List of transactions
        :param datetime: Date and time of block generation
        :param prev_hash: Hash of previous block
        :param public_key: Public key
        """

        self.block_id = block_id
        self.transactions = transactions
        self.datetime = datetime
        self.prev_hash = prev_hash
        self.public_key = public_key
        self.signature = None

    def sha(self) -> int:
        """
        Computes sha256 hash of the block.
        """

        block = self.representation
        sha = hashlib.sha256(block).hexdigest()
        return int(sha, 16)

    # @property
    # def merkle_tree(self):
    #     """
    #     Returns Merkle tree object of transacions
    #     """
    #     return MerkleTree(self.transactions)

    # def transactions_merkle_hash(self):
    #     """
    #     Returns hash of transactions' merkle tree
    #     """
    #     return self.merkle_tree.merkle_root

    def verify_block(self) -> bool:
        """
        Verifies block and all its transactions
        """
        if not verify_signature(self):
            return False

        for transaction in self.transactions:
            if not verify_signature(transaction):
                return False

        return True

    def __str__(self):
        pk = getattr(self, 'public_key', None)
        if pk is not None:
            pk = pk.public_numbers()
            pk = f"{pk.e} {pk.n}"

        return f"""
        Block ID: {self.block_id}\n
        Transactions: {len(self.transactions)}\n
        Hash: {hex(self.sha())}\n
        Last hash: {self.prev_hash}\n
        Datetime: {self.datetime}\n
        Pub key: {pk}\n
        Signature: {self.signature}
        """

    def toJSON(self):
        """
        Serialize block to JSON format
        """
        transactions = [t.toJSON() for t in self.transactions]

        try:
            pub_key = str(numerize_public_key(self))
        except AttributeError:
            pub_key = None

        if self.signature is None:
            signature = None
        else:
            signature = str(self.signature.hex())

        return json.dumps({
            "block_id": self.block_id,
            "transactions": transactions,
            "datetime": self.datetime.timestamp(),
            "prev_hash": self.prev_hash,
            "pub_key": pub_key,
            "signature": signature
        })

    @property
    def representation(self) -> bytes:
        """
        Returns bytes representation of block
        """

        transactions = [t.sha() for t in self.transactions]
        try:
            pub_key = str(numerize_public_key(self))
        except AttributeError:
            pub_key = None

        return bytes(json.dumps({
            "block_id": str(self.block_id),
            "transactions": str(transactions),
            "datetime": self.datetime.timetuple(),
            "prev_hash": str(self.prev_hash),
            "pub_key": pub_key,
        }), 'utf-8')

    def __eq__(self, other):
        if self.transactions != other.transactions:
            return False
        if self.block_id != other.block_id:
            return False
        if self.datetime != other.datetime:
            return False
        if self.prev_hash != other.prev_hash:
            return False
        try:
            if self.public_key.public_numbers() != other.public_key.public_numbers():
                return False
        except AttributeError:
            pass
        return True

    def __ne__(self, other):
        return self.__eq__(other)

    def __repr__(self):
        return str(self)
