from data_creator import save_to_db
import json
from datetime import datetime
from time import sleep
from typing import Dict, List

import py2p
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.backends.openssl.rsa import _RSAPrivateKey
from cryptography.hazmat.primitives.asymmetric import rsa
from merklelib import MerkleTree

from block import Block
from id_bank import ID_bank
from logger import log
from signing import directly_numerize_public_key, numerize_public_key, sign, verify_signature
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

        if self.sock is not None:
            self.nodes = {self.sock.id.decode('utf-8'): 0}
        else:
            self.nodes = None

        self.private_key = Blockchain.generate_private_key()
        self.public_key = Blockchain.generate_public_key(self.private_key)

        # generate private key and public key if not found
        #if not ("private_key.pem" in os.listdir() and "public_key.pem" in os.listdir()):
        #if True:

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

        # self.id_bank = ID_bank(numerize_public_key(self))
        # self.id_bank.update({
        #        numerize_public_key(self):{
        #            "mesh_id": str(getattr(self.sock, 'id', None)),
        #            "score": 0
        #        }
        #    })

    @staticmethod
    def generate_private_key() -> rsa.RSAPrivateKey:
        """
        Generates private key
        """
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

    @staticmethod
    def generate_public_key(private_key: rsa.RSAPrivateKey):
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
        :param d: Dictionary with data
        """
        transaction = Transaction(
            self.public_key,
            d
        )

        return self.add_transaction(transaction)

    def proof_of_authentication(self):
        """
        Chooses miner based on PoAh
        """
        # Peers list
        #nodes = getattr(self, 'nodes', self.id_bank.bank
        #nodes = self.sock.
        

        # Sort potential leaders for bad ones
        #nodes = [peer for peer in nodes if peer["score"] >= 10]
        if self.sock is not None:
            for peer in self.sock.routing_table:
                if peer[2:-1] not in self.nodes.keys():
                    # New peers
                    self.nodes[peer.decode('utf-8')] = 0
        
        # Sort potential leaders for bad ones
        nodes = list(self.nodes.keys())
        nodes = [n for n in nodes if self.nodes[n] >= 15]
        if len(nodes) == 0:
            # No one is a leader!
            # We choose the first one, and give them 10 points
            nodes = list(self.nodes.keys())
            nodes.sort()
            self.nodes[nodes[0]] = 15
            return nodes[0]

        # Choose leader
        time = datetime.now() - self.chain[0].datetime
        leader_n = int(time.total_seconds() % len(nodes))
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
            self.sock.send('mine', str(directly_numerize_public_key(self.public_key)), str(self.sock.id)) # Send out mine order
            miner = self.proof_of_authentication()
            # print(
            #     f"Miner is: {miner[:3]} out of: {[peer[:3] for peer in self.nodes]}")
            my_id = self.sock.id.decode('utf-8')
            # for _peer in self.sock.routing_table:
            #     if not self.id_bank.collection.find_one({'mesh_id': str(_peer)}):
            #         self.id_bank.update({

            #         })
        # Offline
        else:
            my_id = None
            miner = None

        log.debug("MINE_FCN_STARTED",
        extra={
            'mesh_id': str(self.sock.id) if self.sock is not None else None,
        })
        
        if len(self.pending_transactions) > 0:
            # Setup block generation
            new_id = self.last_block.block_id + 1
            prev_hash = self.last_block.sha()
            time = datetime.now()

            # Verify transactions:
            for t in self.pending_transactions:
                if not verify_signature(t):
                    self.pending_transactions.remove(t)
                    print("Removed invalid transaction")
                    if self.sock is not None:
                        self.sock.send('invalid_transaction',
                                        t.sha())
            
            print(f"Pending transactions: {len(self.pending_transactions)}")
            # New block
            block = Block(new_id, self.pending_transactions,
                            time, hex(prev_hash), self.public_key)
            sign(block, self.private_key)

            if my_id == miner:
                log.debug("I_AM_LEADER",
                extra={
                'mesh_id': self.sock.id if self.sock is not None else None,
                })

                # Send out block
                if self.sock is not None:
                    self.sock.send('new_block', block.toJSON())

                self.chain.append(block)
                self.pending_transactions = []

                # Save to db
                save_to_db(block)
                
                print("Mined")
            else:
                log.debug("MINED_NOT_LEADER",
                extra={
                'mesh_id': self.sock.id if self.sock is not None else None,
                })
                if self.sock is not None:
                    self.sock.send('incoming_block', block.toJSON())

    def verify_chain(self) -> bool:
        """
        Verifies if chain is valid
        """
        for i in range(1, len(self.chain)):
            if self.chain[i].prev_hash != hex(self.chain[i-1].sha()):
                return False
            elif not self.chain[i].verify_block():
                return False
            elif self.chain[i].block_id != self.chain[i-1].block_id + 1:
                return False
        return True

    def toJSON(self):
        """
        Serializes chain to JSON format
        """
        return json.dumps([b.toJSON() for b in self.chain])

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

    # @property
    # def blockchain_root(self) -> str:
    #     """
    #     Calculates merkle tree root of the whole blockchain
    #     """
    #     return str(MerkleTree(self.chain).merkle_root)