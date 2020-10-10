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
        self.sock.once('connect', self.once_connect)

    def handle_incoming(self, msg: py2p.base.Message, handler):
        """
        Handles incoming messages
        """
        if msg.packets[0] == 'new_transaction':
            for t in msg.packets[1:]:
                try:
                    self.bc.add_transaction(transaction_fromJSON(t))
                except Exception as e:
                    print(e.with_traceback())
        elif msg.packets[0] == 'mining_finished':
            print("Stop mining! Someone else was first :(")
            # Handle mined notion/block

    def on_connect(self, sock: py2p.MeshSocket):
        print(f"New connection, total: {len(self.sock.routing_table)}")

    def once_connect(self, sock):
        #todo get longest blockchain
        pass
    
    def discovery(self):
        #todo ping same port on every ip on lan
        pass

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == "__main__":
    # Run without arguments
    if len(sys.argv) == 1:
        port = 6000
    # Run with arguments, last is the port nr
    else:
        port = int(sys.argv[-1])

    node = Node(port=port)
    print(bcolors.OKGREEN + "Node setup done." + bcolors.ENDC)

    if port != 6000:
        try:
            node.sock.connect('0.0.0.0', 6000) # todo change when discovery is implmented
        except ConnectionRefusedError:
            print(bcolors.FAIL+"Couldn't connect to peer"+bcolors.ENDC)

    while i:=input():
        if i == 'exit' or i == 'e':
            node.sock.close()
            exit()
        elif i == 'status':
            print(bcolors.OKBLUE+ node.sock.status+bcolors.ENDC)
        elif i == 'peers':
            print(bcolors.OKBLUE+node.sock.routing_table+bcolors.ENDC)
        elif i.startswith('connect '):
            ip, port = i.split(" ")[1].split(':')
            try:
                node.sock.connect(str(ip), int(port))
            except ConnectionRefusedError:
                print(bcolors.FAIL+"Couldn't connect to peer"+bcolors.ENDC)