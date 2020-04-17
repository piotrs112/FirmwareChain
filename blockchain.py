import time
from typing import Dict, Tuple
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from block import Block
from transaction import Transaction


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

        if not ("private_key.pem" in os.listdir() and "public_key.pem" in os.listdir()):
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            public_key = private_key.public_key()

            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            with open('public_key.pem', 'wb') as f:
                f.write(public_pem)

            with open('private_key.pem', 'wb') as f:
                f.write(private_pem)

    @property
    def private_key(self):
        with open("private_key.pem", "rb") as private_key_file:
            return serialization.load_pem_private_key(
                private_key_file.read(),
                password=None,
                backend=default_backend()
            )

    @property
    def public_key(self):
        with open("public_key.pem", "rb") as key_file:
            return serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )

    def add_transaction(self, transaction: Transaction):
        """
        Adds transaction to pending transactions.
        :param transaction: Transaction object
        """

        self.pending_transactions.append(transaction)

    def add_transaction_from_dict(self, d: Dict[str, str]):
        """
        Created transaction from dict and adds it to pending transactions.
        :param d: Dictionary with keys: version, filename, file_hash
        """

        transaction = Transaction(
            self.public_key, 
            d["version"], 
            d["file_hash"],
            d["filename"]
            )
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
            if self.chain[i].prev_hash != self.chain[i-1].compute_hash() or not self.chain[i].compute_hash().startswith('0'*self.DIFFICULTY):
                return False
        return True
