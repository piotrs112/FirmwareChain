import json
from datetime import datetime
from typing import Dict, List

import py2p
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.backends.openssl.rsa import (_RSAPrivateKey)
from cryptography.hazmat.primitives.asymmetric import rsa
from merklelib import MerkleTree

from block import Block
from id_bank import ID_bank
from signing import numerize_public_key, sign, verify_signature
from transaction import Transaction


class Blockchain:
    """
    Stores and manages blocks and transactions
    """

    def __init__(self, sock: py2p.MeshSocket = None):
        """
        Blockchain class constructor
        """

        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        genesis_block = Block(0, [], datetime(2000, 1, 1, 0, 0), "0", None)
        self.chain.append(genesis_block)
        self.sock = sock

        # generate private key and public key if not found
        #if not ("private_key.pem" in os.listdir() and "public_key.pem" in os.listdir()):
        #if True:
        self.private_key = Blockchain.generate_private_key()
        self.public_key = Blockchain.generate_public_key(self.private_key)

            # public_pem = public_key.public_bytes(
            #     encoding=serialization.Encoding.PEM,
            #     format=serialization.PublicFormat.SubjectPublicKeyInfo
            # )

            # private_pem = private_key.private_bytes(
            #     encoding=serialization.Encoding.PEM,
            #     format=serialization.PrivateFormat.PKCS8,
            #     encryption_algorithm=serialization.NoEncryption()
            # )

            # with open('public_key.pem', 'wb') as f:
            #     f.write(public_pem)

            # with open('private_key.pem', 'wb') as f:
            #     f.write(private_pem)

        self.id_bank = ID_bank(numerize_public_key(self))
        self.id_bank.update({
                numerize_public_key(self):{
                    "mesh_id": str(getattr(self.sock, 'id', None)),
                    "score": 10
                }
            })
        

    # @property
    # def private_key(self) -> _RSAPrivateKey:
    #     """
    #     Returns private key object
    #     """
    #     with open("private_key.pem", "rb") as private_key_file:
    #         return serialization.load_pem_private_key(
    #             private_key_file.read(),
    #             password=None,
    #             backend=default_backend()
    #         )

    # @property
    # def public_key(self) -> _RSAPublicKey:
    #     """
    #     Returns public key object
    #     """
    #     with open("public_key.pem", "rb") as key_file:
    #         return serialization.load_pem_public_key(
    #             key_file.read(),
    #             backend=default_backend()
    #         )

    @staticmethod
    def generate_private_key() -> _RSAPrivateKey:
        """
        Generates private key
        """
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

    @staticmethod
    def generate_public_key(private_key: _RSAPrivateKey):
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
                self.sock.send('new_transaction', transaction.toJSON())
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
        # Peers list
        nodes = getattr(self, 'nodes', self.id_bank.bank)

        # Sort potential leaders for bad ones
        nodes = [peer["pubkey"] for peer in nodes if peer["score"] >= 10]

        # Choose leader at 10-seconds intervals
        time = datetime.now() - self.chain[0].datetime
        leader_n = int(time.total_seconds() % len(nodes)) #/10 % len(nodes))
        nodes.sort()

        return nodes[leader_n]

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
            self.sock.send('mine') # Send out mine order
            miner = self.proof_of_authority()
            # print(
            #     f"Miner is: {miner[:3]} out of: {[peer[:3] for peer in self.nodes]}")
            my_id = self.sock.id.decode('utf-8')
        # Offline
        else:
            my_id = None
            miner = None

        if my_id == miner:
            # delta = datetime.now() - self.last_block.datetime
            # if delta.total_seconds() < 3 and self.last_block.public_key == self.public_key:
            #     # Too fast!
            #     return
            
            #el--v
            if len(self.pending_transactions) > 0:
                # Setup block generation
                new_id = self.last_block.block_id + 1
                prev_hash = self.last_block.compute_hash()
                time = datetime.now()

                # Verify transactions:
                for t in self.pending_transactions:
                    if not verify_signature(t):
                        self.pending_transactions.remove(t)
                        print("Removed invalid transaction")
                        if self.sock is not None:
                            self.sock.send('invalid_transaction',
                                            t.numerize_public_key())
                
                print(f"Pending transactions: {len(self.pending_transactions)}")
                # New block
                block = Block(new_id, self.pending_transactions,
                              time, prev_hash, self.public_key)
                sign(block, self.private_key)

                # Send out block
                if self.sock is not None:
                    self.sock.send('new_block', block.toJSON())
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
            elif self.chain[i].block_id != self.chain[i-1].block_id + 1:
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
