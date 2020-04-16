import hashlib
import json
from typing import List, Dict


class Block:
    """
        Block class.
    """

    def __init__(self, block_id: int, transactions: List[Dict[str,str]], datetime: str, prev_hash: str):
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

        block = json.dumps(self.__dict__, sort_keys=True)
        sha = hashlib.sha256(block.encode()).hexdigest()
        return sha

    def __str__(self):
        return f"Block ID: {self.block_id}\nTransactions: {len(self.transactions)}\nHash: {self.compute_hash()}\nLast hash: {self.prev_hash}\n"
