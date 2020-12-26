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
from merklelib import MerkleTree

from block import Block
from signing import verify_signature, sign
from transaction import Transaction


class Blockchain:
    """
    Stores and manages blocks and transactions
    """

    def __init__(self, sock: py2p.MeshSocket = None):
        """
        Blockchain class constructor
        """

        self.chain = []
        self.pending_transactions = []
        genesis_block = Block(0, [], datetime(2000, 1, 1, 0, 0), "0", None)
        self.chain.append(genesis_block)
        self.sock = sock

        if self.sock is not None:
            self.nodes = {self.sock.id.decode('utf-8'): 10}
        else:
            self.nodes = None

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
        :param private_key: Private key to generate public key from
        """
        return private_key.public_key()

    def add_transaction(self, transaction: Transaction) -> bool:
        """
        Adds transaction to pending transactions.
        :param transaction: Transaction object
        """
        if verify_signature(transaction):
            self.pending_transactions.append(transaction)
            if self.sock is not None:
                self.sock.send(transaction.toJSON(), type='new_transaction')
            return True
        else:
            return False

    def add_transaction_from_dict(self, d: Dict[str, str]) -> bool:
        """
        Creates transaction from dict and adds it to pending transactions.
        :param d: Dictionary with keys: version, filename, file_hash
        """
        transaction = Transaction(
            self.public_key,
            d["version"],
            d["file_hash"],
            d["filename"]
        )

        return self.add_transaction(transaction)

    def proof_of_authority(self):
        """
        Chooses miner based on their authority
        """
        # Update peer list
        if self.sock is not None:
            for peer in self.sock.routing_table:
                if peer.decode('utf-8') not in self.nodes:
                    self.nodes[peer.decode('utf-8')] = 10

        # Sort potential leaders for bad ones
        nodes = list(self.nodes.keys())
        nodes = [n for n in nodes if self.nodes[n] >= 10]

        # Choose leader at 10-seconds intervals
        time = datetime.now() - self.chain[0].datetime
        last_second = int(str(time.seconds)[-1])
        time = int(time.total_seconds()) - last_second
        leader_n = time % len(nodes)
        nodes.sort()

        leader = nodes[leader_n]

        # if self.sock is not None:
        #     self.sock.send(b'whisper', ('miner', miner))

        return leader

    @property
    def last_block(self) -> Block:
        """
        Returns the last block of the chain
        """

        return self.chain[-1]

    def mine(self):
        """
        Mines a new block with a Proof of Authority and adds it to the chain.
        """
        # Online
        if self.sock is not None:
            miner = self.proof_of_authority()  # todo check if all choose the same one
            print(
                f"Miner is: {miner[:3]} out of: {[peer[:3] for peer in self.nodes]}")
            my_id = self.sock.id.decode('utf-8')
        # Offline
        else:
            my_id = None
            miner = None

        if my_id == miner:
            if len(self.pending_transactions) > 0:
                # Setup block generation
                new_id = self.last_block.block_id + 1
                prev_hash = self.last_block.compute_hash()
                time = datetime.now()

                # Verify transactions:
                for t in self.pending_transactions:
                    if not verify_signature(t):
                        self.pending_transactions.remove(t)
                        if self.sock is not None:
                            self.sock.send(t.numerize_public_key(),
                                           type='invalid_transaction')

                # New block
                block = Block(new_id, self.pending_transactions,
                              time, prev_hash, self.public_key)
                sign(block, self.private_key)

                # Send out block
                if self.sock is not None:
                    self.sock.send(block.toJSON(), type='mined')
                self.chain.append(block)
                self.pending_transactions = []
                print("Mined")

    def verify_chain(self) -> bool:
        """
        Verifies if chain is valid
        """
        for i in range(1, len(self.chain)):
            if self.chain[i].prev_hash != self.chain[i-1].compute_hash():
                return False
            elif not self.chain[i].verify_block():
                return False
        return True

    @property
    def blockchain_root(self) -> str:
        """
        Calculates merkle tree root of the whole blockchain
        """
        return MerkleTree(self.chain).merkle_root

    def toJSON(self):
        """
        Serializes chain to JSON format
        """
        return json.dumps([b.toJSON() for b in self.chain])
