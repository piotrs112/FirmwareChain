import sys

import py2p

from blockchain import Blockchain
from data_manipulation import transaction_fromJSON


class Node:
    """
    Combining blockchain with secure P2P connectivity
    """

    def __init__(self, port=4444):
        self.sock = py2p.MeshSocket('0.0.0.0', port, py2p.Protocol('mesh', 'SSL'))
        self.bc = Blockchain(self.sock)
        self.sock.register_handler(self.handle_incoming)

        # Attach listener to connection event
        self.sock.on('connect', self.on_connect)

    def handle_incoming(self, msg: py2p.base.Message, handler):
        """
        Handles incoming messages
        """
        print("I got sth")
        print(msg.packets)
        if msg.packets[0] == 'new_transaction':
            for t in msg.packets[1:]:
                try:
                    self.bc.add_transaction(transaction_fromJSON(t))
                except Exception as e:
                    print(e.with_traceback())
        elif msg.packets[0] == 'mining_finished':
            print("Stop mining! Someone else was first :(")

    def on_connect(self, socket: py2p.MeshSocket):
        print(f"New connection, total: {len(socket.routing_table)}")