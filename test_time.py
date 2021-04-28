import datetime
from signing import sign
import timeit

from blockchain import Blockchain
from block import Block
from transaction import Transaction

import pprint

pk = Blockchain.generate_private_key()
pub_k = pk.public_key()

t_l = [Transaction(pub_k,
        {"add":{
            "1234": "some_door"
            }
        }) for i in range(10)
        ]

def sign_transaction():
    sign(t_l[0], pk)

def test_timing_signing():
    # time = timeit.timeit(sign_transaction, number=1000)
    # print(f"Transaction signing x1000: {time}s\t avg: {time/1000}")
    for t in t_l[1:]:
        sign(t, pk)
    
   # b = Block(0, t_l, datetime.datetime.now(), "0", pub_k)
    # time = timeit.timeit('sign(b, pk)',setup='b = Block(0, t_l, datetime.datetime.now(), "0", pub_k)', number=1000, globals=globals())
    # print(f"Block signing x1000: {time}s\t avg: {time/1000}")


if __name__ == "__main__":
    test_timing_signing()
    ptprint = pprint.PrettyPrinter().pprint
    ptprint(Block(0, [Transaction(pub_k, {"test": "data"})], datetime.datetime.now(), "0", pub_k).toJSON())