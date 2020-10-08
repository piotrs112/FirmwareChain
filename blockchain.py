from datetime import datetime
from typing import Dict, Tuple
import os
import json

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends.openssl.rsa import (_RSAPrivateKey,
                                                      _RSAPublicKey)
import py2p

from block import Block
from transaction import Transaction


class Blockchain:
    DIFFICULTY = 2 # Number of leading zeros required in hash

    def __init__(self, sock: py2p.MeshSocket):
        """
        Blockchain class constructor
        """

        self.chain = []
        self.pending_transactions = []
        genesis_block = Block(0, [], datetime.now(), "0")
        genesis_block, new_hash = self.proof_of_work(genesis_block)
        self.chain.append(genesis_block)
        self.sock = sock

        # generate private key and public key if not found
        if not ("private_key.pem" in os.listdir() and "public_key.pem" in os.listdir()):
            private_key = Blockchain.generate_private_key()
            public_key = Blockchain.generate_public_key(private_key)

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
    def private_key(self) -> _RSAPrivateKey:
        """
        Returns private key object
        """
        with open("private_key.pem", "rb") as private_key_file:
            return serialization.load_pem_private_key(
                private_key_file.read(),
                password=None,
                backend=default_backend()
            )

    @property
    def public_key(self) -> _RSAPublicKey:
        """
        Returns public key object
        """
        with open("public_key.pem", "rb") as key_file:
            return serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )

    @classmethod
    def generate_private_key(cls) -> _RSAPrivateKey:
        """
        Generates private key
        """
        return rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
    
    @classmethod
    def generate_public_key(cls, private_key: _RSAPrivateKey):
        """
        Generates public key
        """
        return private_key.public_key()

    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Adds transaction to pending transactions.
        :param transaction: Transaction object
        """
        if transaction.verify():
            self.pending_transactions.append(transaction)
            self.sock.send(transaction.toJSON(), type='new_transaction')
            return True
        else: return False

    def add_transaction_from_dict(self, d: Dict[str, str]) -> bool:
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
            
        return self.add_transaction(transaction)

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

        if len(self.pending_transactions) > 0:
            new_id = self.last_block.block_id + 1
            prev_hash = self.last_block.compute_hash()
            time = datetime.now()

            block = Block(new_id, self.pending_transactions,
                          time, prev_hash)
            block, new_hash = self.proof_of_work(block)
            #Send out block
            self.sock.send(block, flag='mined')

            self.chain.append(block)
            self.pending_transactions = []

    def verify_chain(self) -> bool:
        """
        Verifies if chain is valid
        """
        for i in range(1, len(self.chain)):
            if self.chain[i].prev_hash != self.chain[i-1].compute_hash():
                return False
            elif not self.chain[i].compute_hash().startswith('0'*self.DIFFICULTY):
                return False
            elif not self.chain[i].verify_block():
                return False
        return True
        
    def toJSON(self):
        """
        Serializes chain to JSON format
        """
        return json.dumps([b.toJSON() for b in self.chain])
