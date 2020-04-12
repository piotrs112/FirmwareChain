import hashlib
import json


class Block:
    def __init__(self, id: int, transactions: list, datetime: str,prev_hash: str):
        self.id = id
        self.transactions = transactions
        self.datetime = datetime
        self.prev_hash = prev_hash
    
    def compute_hash(self) -> str:
        block = json.dumps(self.__dict__, sort_keys=True)
        sha = hashlib.sha256(block.encode()).hexdigest()
        return sha
