import time
from typing import Tuple, Dict

from block import Block


class Blockchain:
    DIFFICULTY = 2

    def __init__(self):
        """
        Blockchain class constructor
        """

        self.chain = []
        self.pending_transactions = []
        genesis_block = Block(0, [], "0", "0")
        self.chain.append(genesis_block)

    def add_transaction(self, transaction: Dict[str, str]):
        """
        Adds transaction to pending transactions.
        :param transaction: Dictionary with keys: version, filename, file_hash
        """

        self.pending_transactions.append(transaction)

    def proof_of_work(self, block) -> Tuple[Block, str]:
        """
        Computes hash until it has a proper number of leading zeros by increasing nonce.
        """
        computed = block.compute_hash()
        while not computed.startswith('0' * self.DIFFICULTY):
            block.nonce = block.nonce + 1
            computed = block.compute_hash()
        return block, computed

    @property
    def last_block(self) -> Block:
        """
        Returns the last block of the chain
        """

        return self.chain[-1]

    def mine(self):
        """
        Mines a new block with a Proof of Work and adds it to the chain.
        """

        if self.pending_transactions != []:
            new_id = self.last_block.block_id + 1
            prev_hash = self.last_block.compute_hash()
            block = Block(new_id, self.pending_transactions,
                          str(time.time()), prev_hash)
            block, new_hash = self.proof_of_work(block)
            self.chain.append(block)
            self.pending_transactions = []

    def verify_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            if self.chain[i].prev_hash != self.chain[i-1].compute_hash():
                return False
        return True
