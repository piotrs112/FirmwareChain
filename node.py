#!/usr/bin/env python3
import sys

import py2p

from blockchain import Blockchain
from transaction import Transaction
from data_manipulation import transaction_fromJSON, fromJSON


def exit_function():
    """
    Close connection safely and exit
    """
    node.sock.close()
    exit()


class Node:
    """
    Combining blockchain with secure P2P connectivity
    """

    def __init__(self, port=4444):
        """
        Initialize node.
        :param port: Port on which the node's socket will be operating
        """
        self.sock = py2p.MeshSocket(
            '0.0.0.0', port, py2p.Protocol('mesh', 'SSL'))
        self.bc = Blockchain(self.sock)
        self.sock.register_handler(self.handle_incoming)

        # Attach listener to connection event
        self.sock.on('connect', self.on_connect)
        self.sock.once('connect', self.once_connect)

        self.longest_chain = 1
        self.longest_chain_owner = None

    def handle_incoming(self, msg: py2p.base.Message, handler):
        """
        Handles incoming messages
        :param msg: Incoming message
        :param handler: Handler function
        """

        print(msg.packets)  # todo del after dev

        # Add new transaction
        if msg.packets[0] == 'new_transaction':
            for t in msg.packets[1:]:
                try:
                    transaction = transaction_fromJSON(t)
                    if transaction not in self.bc.pending_transactions:
                        self.bc.add_transaction(transaction)
                except Exception as e:
                    print(e.with_traceback())

        # Mined new block
        elif msg.packets[0] == 'mined':
            new_block = fromJSON(msg.packets[1])
            if new_block.verify_block():
                node.bc.chain.append(new_block)
                for t in node.bc.pending_transactions:
                    if t in new_block.transactions:
                        node.bc.pending_transactions.remove(t)
            else:
                print(bcolors.FAIL + "Invalid block!" + bcolors.ENDC)

        # Someone asking for chain length
        elif msg.packets[0] == 'get_chain_length':
            msg.reply(type=b'whisper', packets=len(
                self.bc.chain), sender=msg.sender)

        # Someone sending chain length
        elif msg.packets[0] == 'set_chain_length':
            # todo podmiana od razu czy po czasie?
            if msg.packets[1] > self.longest_chain:
                self.longest_chain = msg.packets[1]
                self.longest_chain_owner == msg.sender

                print(f"{self.longest_chain} {self.longest_chain_owner}")

    def on_connect(self, sock: py2p.MeshSocket):
        """
        What to do on every single new connection
        :param sock: Mesh socket object
        """
        print(
            f"New connection, total: {len(self.sock.routing_table)}")  # todo fix len()

    def once_connect(self, sock: py2p.MeshSocket):
        """
        What to do on the first connections
        :param sock: Mesh socket object
        """
        self.sock.send(type='get_chain_length')


class bcolors:
    """
    Color helpers for displaying data in console
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


if __name__ == "__main__":
    """
    Main function run at script execution
    """
    # Run without arguments
    if len(sys.argv) == 1:
        port = 6000
    # Run with arguments, last is the port nr
    else:
        port = int(sys.argv[-1])

    # Communications setup
    node = Node(port=port)
    print(bcolors.OKGREEN + "Node setup done." + bcolors.ENDC)

    if port != 6000:
        try:
            node.sock.connect('0.0.0.0', 6000)
        except ConnectionRefusedError:
            print(bcolors.FAIL+"Couldn't connect to peer"+bcolors.ENDC)

    # Console handler
    try:
        while True:
            i = input()
            if i == 'h' or i == 'help':
                print(bcolors.BOLD +
                      """
                exit
                status
                peers
                connect <ip_address:port>
                id
                msg <params>
                stats
                mine
                add_test_transaction
                """+bcolors.ENDC)

            elif i == 'exit' or i == 'e' or i == 'quit' or i == 'q':
                exit_function()

            elif i == 'status':
                print(bcolors.OKBLUE + str(node.sock.status) + bcolors.ENDC)

            elif i == 'peers':
                print(bcolors.OKBLUE + str([str(k)[2:-1]
                                            for k in node.sock.routing_table]) + bcolors.ENDC)

            elif i.startswith('connect '):
                try:
                    ip, port = i.split(" ")[1].split(':')
                except ValueError:
                    ip = "localhost"
                    port = i.split(" ")[1]

                try:
                    node.sock.connect(str(ip), int(port))
                except ConnectionRefusedError:
                    print(bcolors.FAIL + "Couldn't connect to peer" + bcolors.ENDC)

            elif i == 'id':
                print(bcolors.OKBLUE + str(node.sock.id)[2:-1] + bcolors.ENDC)

            elif i == 'stats':
                print(bcolors.OKBLUE + "Chain: " + str(node.bc.chain))
                print("Pending: " + str(node.bc.pending_transactions) + bcolors.ENDC)

            elif i.startswith("msg"):
                m = i.split(" ")
                node.sock.send(packets=[str(j) for j in m[1:]], type=str(m))

            elif i == 'mine':
                node.bc.mine()

            elif i == 'add_test_transaction' or i == 't':
                transaction = Transaction(
                    node.bc.public_key, "test", "hash", "test.name")
                transaction.sign(node.bc.private_key)
                node.bc.add_transaction(transaction)
                print(bcolors.OKBLUE + "Transaction added" + bcolors.ENDC)

            elif i == 'last block' or i == 'lb':
                print(node.bc.last_block.toJSON())

            elif i == '':
                pass

            else:
                print(bcolors.FAIL + "Wrong command." + bcolors.ENDC)

    except Exception as e:
        if type(e) is KeyboardInterrupt:
            exit_function()
        else:
            print(e.with_traceback())
