import time

from block import Block


class Blockchain:
    def __init__(self):
        """
        Blockchain class constructor
        """

        self.chain = []
        self.pending_transactions = []
        genesis_block = Block(0,[],"0","0")
        self.chain.append(genesis_block)

    def add_transaction(self, transaction: dict):
        """
        Adds transaction to pending transactions.
        :param transaction: Dictionary with keys: version, filename, file_hash
        """

        self.pending_transactions.append(dict)

    def last_block(self) -> Block:
        """
        Returns the last block of the chain
        """

        return self.chain[-1]

    
