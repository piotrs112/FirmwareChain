from random import choice, randint
from time import sleep

from node import Node
from signing import directly_numerize_public_key, sign
from transaction import Transaction


def test_init():
    n = Node()
    assert n.sock.status == "Nominal"


def test_connection():
    port = randint(6002, 6100)
    port2 = port + 1

    n = Node(port=port)
    n2 = Node(port=port2)

    n.sock.connect("0.0.0.0", port=port2)
    sleep(0.1)

    assert n.sock.id in [peer for peer in n2.sock.routing_table]
    assert n2.sock.id in [peer for peer in n.sock.routing_table]

    assert n.sock.status == "Nominal"

def test_id_map():
    port = randint(6002, 6100)
    port2 = port + 1

    n = Node(port=port)
    n2 = Node(port=port2)

    n.sock.connect("0.0.0.0", port=port2)
    sleep(0.1)

    id_1 = {directly_numerize_public_key(n.bc.public_key): str(n.sock.id)}
    id_2 = {directly_numerize_public_key(n2.bc.public_key): str(n2.sock.id)}
    
    assert n.id_pk_map == {directly_numerize_public_key(n.bc.public_key): str(n.sock.id)}
    assert n2.id_pk_map == {directly_numerize_public_key(n2.bc.public_key): str(n2.sock.id)}

    n2.passport()
    sleep(0.1)

    assert n.id_pk_map.get(directly_numerize_public_key(n2.bc.public_key)) == str(n2.sock.id)
    assert n2.id_pk_map.get(directly_numerize_public_key(n.bc.public_key)) == str(n.sock.id)

def test_transaction_propagation():
    port = randint(6002, 6100)
    port2 = port + 1

    server = Node(port)
    node = Node(port2)

    node.sock.connect("0.0.0.0", port=port)
    sleep(0.1)

    t = Transaction(server.bc.public_key, {'test': 'data'})
    sign(t, server.bc.private_key)
    server.bc.add_transaction(t)

    sleep(0.5)
    assert node.bc.pending_transactions[0] == t

    assert node.sock.status == "Nominal"

def test_mining():
    n_nodes = 4
    nodes = {}
    
    for port in range(n:=randint(6000,7000), n + n_nodes):
        nodes[port] = Node(port=port)

    for port, node in nodes.items():
        try:
            node.sock.connect("0.0.0.0", port=port+1)
        except Exception as e:
            print("Didnt connect", e)
            pass

    sleep(1)

    vals = list(nodes.values())
    for i in range(3):
        server = None
        for j in range(3):
            server = choice(vals)
            t = Transaction(server.bc.public_key, {f'test_{i}': f'data_{i}'})
            sign(t, server.bc.private_key)
            server.bc.add_transaction(t)
            sleep(0.1)
        server.sock.send('mine')
        sleep(0.1)

    node0 = vals[0]
        
    for node in vals[1:]:
        assert node.bc.chain == node0.bc.chain

    for node in vals:
        assert node.sock.status == "Nominal"
