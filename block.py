import hashlib
import json
from typing import Dict, List
from datetime import datetime

from merklelib import MerkleTree

from transaction import Transaction


class Block:
    """
        Block class.
    """

    def __init__(self, block_id: int, transactions: List[Transaction], datetime: datetime, prev_hash: str):
        """
        Block class constructor
        :param block_id: ID of the block, unique
        :param transactions: List of transactions
        :param datetime: Date and time of block generation
        :param prev_hash: Hash of previous block
        :param nonce: Parameter to change block hash.
        """

        self.block_id = block_id
        self.transactions = transactions
        self.datetime = datetime
        self.prev_hash = prev_hash
        self.nonce = 0

    def compute_hash(self) -> str:
        """
        Computes sha256 hash of the block.
        """

        #block = json.dumps(self.representation, sort_keys=True)
        block = self.toJSON()
        sha = hashlib.sha256(block.encode()).hexdigest()
        return sha
    
    def verify_block(self) -> bool:
        """
        Verifies block and all its transactions
        """
        
        for transaction in self.transactions:
            if not transaction.verify():
                return False
                
        return True

    @property
    def merkle_root(self):
        """
        Returns a merkle root of the transaction hashes.
        """

        tree = MerkleTree(self.transactions)
        return tree.merkle_root

    def __str__(self):
        return f"Block ID: {self.block_id}\nTransactions: {len(self.transactions)}\nHash: {self.compute_hash()}\nLast hash: {self.prev_hash}\n"

    def toJSON(self):
        """
        Serialize block to JSON format
        """
        transactions = [t.toJSON() for t in self.transactions]

        return json.dumps({
            "block_id": self.block_id,
            "transactions": transactions,
            "datetime": self.datetime.timestamp(),
            "prev_hash": self.prev_hash,
            "nonce": self.nonce
        })
    
    def __repr__(self):
        return str(self)