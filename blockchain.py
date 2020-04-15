import time

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

    def add_transaction(self, transaction: dict):
        """
        Adds transaction to pending transactions.
        :param transaction: Dictionary with keys: version, filename, file_hash
        """

        self.pending_transactions.append(transaction)

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

        new_id = self.last_block.block_id + 1
        prev_hash = self.last_block.compute_hash()
        block = Block(new_id, self.pending_transactions,
                      str(time.time()), prev_hash)
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.DIFFICULTY):
            block.nonce = block.nonce + 1
            computed_hash = block.compute_hash()

        self.chain.append(block)