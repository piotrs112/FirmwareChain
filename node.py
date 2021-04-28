#!/usr/bin/env python3
from block import Block
import random
import sys
from time import sleep

import py2p

from blockchain import Blockchain
from data_manipulation import fromJSON, transaction_fromJSON
from logger import log
from signing import (directly_numerize_public_key, numerize_public_key, sign,
                     verify_signature)
from transaction import Transaction
from data_creator import add_one, remove_one, save_to_db


def exit_function(node):
    """
    Close connection safely and exit
    """
    node.sock.close()
    exit()


class Node:
    """
    Combining blockchain with secure P2P connectivity
    """

    def __init__(self, port=6000):
        """
        Initialize node.
        :param port: Port on which the node's socket will be operating
        """
        self.sock = py2p.MeshSocket(
            '0.0.0.0', port, py2p.Protocol('mesh', 'SSL'))
        
        self.type = "trusted" if port == 6000 else "normal"

        self.connection = py2p.mesh.MeshConnection(
            sock=self.sock, server=self.sock)

        self.bc = Blockchain(self.sock)

        # Attach listener to connection event
        #self.sock.on('connect', self.on_connect)
        #self.sock.once('connect', self.once_connect)
        self.sock.on('message', self.handle_incoming)

        self.incoming_blocks = []
        self.id_pk_map = {directly_numerize_public_key(self.bc.public_key): str(self.sock.id)}

    def handle_incoming(self, connection) -> bool:
        """
        Handles incoming messages
        :param connection: Connection object
        """
        # Raise exceptions, dont hide them
        if self.sock.status != "Nominal":
            raise Exception(self.sock.status[0])

        msg = connection.recv()
        #print(msg.packets)
        packets = msg.packets[1:]
        # Add new transaction
        if packets[0] == 'new_transaction':
            log.debug(
                "GOT_NEW_TRANSACTION",
                extra={
                'node': numerize_public_key(self.bc),
                'data': packets[1]
                })
            
            print("new transaction received")
            t = packets[1]
            #try:
            transaction = transaction_fromJSON(t)
            if transaction not in self.bc.pending_transactions:
                if verify_signature(transaction):
                    self.bc.add_transaction(transaction)
                else:
                    # Punish for invalid transaction
                    #self.bc.id_bank.modify(transaction.public_key, -2)
                    self.punish(2, transaction)

            #except Exception as e:
            #    print(e.with_traceback())

        # Mined new block
        elif packets[0] == 'new_block':
            log.debug("GOT_NEW_BLOCK",
                extra={
                'mesh_id': self.sock.id,
                'data': packets[1]
                })

            new_block = fromJSON(packets[1])
            if new_block not in self.bc.chain:
                if new_block.verify_block():
                    self.bc.chain.append(new_block)
                    if not self.bc.verify_chain():
                        self.bc.chain.remove(new_block)
                        # Punish for invalid block
                        #self.bc.id_bank.modify(new_block.public_key, -5)
                        self.punish(5, new_block)
                    else:
                        # for t in self.bc.pending_transactions:
                        #     if t in self.bc.last_block.transactions:
                        #         self.bc.pending_transactions.remove(t)
                        self.bc.pending_transactions = []

                        # Reward for valid block
                        blocks_to_reward = [b for b in self.incoming_blocks if b.datetime < new_block.datetime]
                        for block in blocks_to_reward:
                            self.reward(1, block)
                        
                        # Save to db
                        save_to_db(new_block)
                else:
                    print(bcolors.FAIL + "Invalid block!" + bcolors.ENDC)
                    print(new_block)
                    # Punish for invalid block
                    #self.bc.id_bank.modify(new_block.public_key, -5)
                    self.punish(5, new_block)

        # Incoming blocks before signing
        elif packets[0] == 'incoming_block':
            log.debug("GOT_INCOMING",
                extra={
                'mesh_id': self.sock.id,
                'data': packets[1]
                })
            self.incoming_blocks.append(fromJSON(packets[1]))

        # Someone asking for chain length
        # elif packets[0] == 'get_chain_length':
        #     msg.reply(type=b'whisper', packets=len(
        #         self.bc.chain), sender=msg.sender)

        # Someone sending chain length
        # elif packets[0] == 'set_chain_length':
        #     # todo podmiana od razu czy po czasie?
        #     if packets[1] > self.longest_chain:
        #         self.longest_chain = packets[1]
        #         self.longest_chain_owner = msg.sender

        #         print(f"{self.longest_chain} {self.longest_chain_owner}")

        # Start mining
        elif packets[0] == 'mine':
            log.debug("START_MINING")
            self.bc.mine()
            #print(f"Got mine order!")

        # Update new node in id bank
        elif packets[0] == 'passport':
            print("PASSPORT")
            print({packets[2][2:-1]: 0})
            # self.bc.id_bank.update({
            #     packets[1]: {
            #         "mesh_id": str(packets[2]),
            #         "score": 10
            #     }
            # })
            self.id_pk_map.update({packets[1]: packets[2][2:-1]})
            self.bc.nodes.update({packets[2][2:-1]: 0})
            self.passport()

        return True

    def on_connect(self, sock: py2p.MeshSocket):
        """
        What to do on every single new connection
        :param sock: Mesh socket object
        """
        print(
            f"New connection, total: {len(str([str(k)[2:-1] for k in self.sock.routing_table]))}")
        sleep(1)
        print("on _con")
        self.passport()
        #todo get it working

    def once_connect(self, sock: py2p.MeshSocket):
        """
        What to do on the first connections
        :param sock: Mesh socket object
        """
        print("once")

    def passport(self):
        self.sock.send('passport', numerize_public_key(self.bc), str(self.sock.id))
    
    def reward(self, points, o: object):
        if points == 0:
            return

        #other_mesh_id = str(self.bc.nodes[self.id_pk_map[numerize_public_key(o)]].decode('utf-8'))[2:-1]

        if points > 0:
            _msg = "REWARD"
        else:
            _msg = "PUNISH"

        log.debug(_msg,
                extra={
                'mesh_id': self.sock.id,
                #'other_mesh_id': other_mesh_id
                })
        # try:
        score = self.bc.nodes.get(self.id_pk_map[numerize_public_key(o)], None)
        
        if score is not None:
            score += points
            
            if score > 30:
                score = 30
            elif score < 0:
                score = 0
            
            self.bc.nodes[self.id_pk_map[numerize_public_key(o)]] = score


    def punish(self, points, o: object):
        self.reward(-points, o)


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


def main():
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
    
    node.passport()

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
                exit_function(node)

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
                node.sock.send([str(j) for j in m[1:]])

            elif i == 'mine' or i == 'm':
                node.sock.send('mine')

            elif i == 'add_test_transaction' or i == 't':
                num = random.randint(1, 100)
                transaction = Transaction(
                    node.bc.public_key, {'test': 'manual'})
                sign(transaction, node.bc.private_key)
                node.bc.add_transaction(transaction)
                print(bcolors.OKBLUE + "Transaction added" + bcolors.ENDC)
            
            elif i.startswith('add'):
                try:
                    _, uuid, door = i.split(' ')
                except ValueError:
                    uuid = "446176000983"
                    door = "door1"

                transaction = Transaction(
                    node.bc.public_key,
                    add_one(str(uuid), door)
                    )
                sign(transaction, node.bc.private_key)
                node.bc.add_transaction(transaction)
                print(bcolors.OKBLUE + f"{uuid} @ {door} added" + bcolors.ENDC)
            
            elif i.startswith('rm'):
                try:
                    _, uuid, door = i.split(' ')
                except ValueError:
                    uuid = "446176000983"
                    door = "door1"

                transaction = Transaction(
                    node.bc.public_key,
                    remove_one(str(uuid), door)
                    )
                sign(transaction, node.bc.private_key)
                node.bc.add_transaction(transaction)
                print(bcolors.OKBLUE + f"{uuid} @ {door} removed" + bcolors.ENDC)

            elif i == 'last block' or i == 'lb':
                print(node.bc.last_block.toJSON())

            elif i == '':
                pass
            elif i == 'u':
                print(node.bc.nodes)
            elif i == 'mm':
                node.sock.send('mm', 'Hi!')
            elif i.startswith('> '):
                command = i.lstrip("> ")
                try:
                    exec(command)
                except Exception as e:
                    print(e)
            #elif i == "bank":
            #    print(node.bc.id_bank.bank)
            elif i == "passport":
                node.passport()
            elif i == "map":
                print(node.id_pk_map)
            elif i == "points":
                print(node.bc.nodes)
            else:
                print(bcolors.FAIL + "Wrong command." + bcolors.ENDC)

    except Exception as e:
        if type(e) is KeyboardInterrupt:
            exit_function(node)
        else:
            print(e)


if __name__ == "__main__":
    main()
