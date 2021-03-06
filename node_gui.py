import json
import random
import sys
from datetime import datetime

import py2p
from cryptography.hazmat.backends.openssl.rsa import (_RSAPrivateKey,
                                                      _RSAPublicKey)
from flask import Flask, render_template, request

from blockchain import Blockchain
from data_manipulation import get_chain
from node import Node
from transaction import Transaction

app = Flask(__name__, template_folder="interface", static_folder="interface")

if len(sys.argv) == 1:
    port = 5000
else:
    port = int(sys.argv[-1])


node = Node(port=int(port+1000))
if port != 5000:
    node.sock.connect('0.0.0.0', 6000)
b = node.bc

@app.route('/', methods=['GET'])
def index():
    """
    Returns index page
    """

    data = [] # Stores data for tables
    head = b.chain[0].__dict__.keys() # Blockchain table headers

    # Prepare blocks data for table
    for block in b.chain:
        line = []
        for v in block.__dict__.values():
            if type(v) is datetime:
                line.append(v.strftime("%d/%m/%Y, %H:%M:%S"))
            elif type(v) is list:
                line.append(len(v))
            else:
                line.append(v)
        data.append(line)

    # Prepare pending tansactions data for table
    if len(b.pending_transactions) > 0:
        t_h = b.pending_transactions[0].__dict__.keys()
        p_t = []
        for t in b.pending_transactions:
            line = []
            for v in t.__dict__.values():
                if type(v) is _RSAPublicKey:
                    if t.is_signed:
                        signed = "Signed"
                    else:
                        signed = "Not signed"
                    line.append(signed)
                elif type(v) is bytes:
                    line.append(hash(v))
                else:
                    line.append(v)
            p_t.append(line)
    else: # if there are no pending transactions
        t_h = []
        p_t = []

    # Renders the website
    return render_template("index.html",
                           blocks=data,
                           head=head,
                           transactions_head=t_h,
                           pending_transactions=p_t)

@app.route("/network/")
def network():
    return render_template('network.html', peers=node.sock.routing_table)

@app.route("/raw/")
def raw():
    data = []
    head = b.chain[0].__dict__.keys()
    for block in b.chain:
        line = []
        for v in block.__dict__.values():
            line.append(v)
        data.append(line)

    if len(b.pending_transactions) > 0:
        t_h = b.pending_transactions[0].__dict__.keys()
        p_t = []
        for t in b.pending_transactions:
            line = []
            for v in t.__dict__.values():
                line.append(v)
            p_t.append(line)
    else:
        t_h = []
        p_t = []

    return json.dumps({"blocks": str(data),
                       "head": str(head),
                       "transactions_head": t_h,
                       "pending_transactions": p_t})


@app.route('/rest/', methods=['POST'])
def rest_api():
    """
    REST API for interacting with node
    """
    try:
        action = request.json['action']
        print(action)
        req = request.json
        print(request.remote_addr, request.environ['REMOTE_PORT'])
        if action == "get_chain":
            return b.toJSON()
        
        elif action == "get_peers":
            return json.dumps(node.sock.routing_table)

        elif action == "add_transaction":
            data = req["transaction"]
            t = Transaction(
                b.public_key, data['version'], data['file_hash'], data['filename'])
            t.sign(b.private_key)
            b.add_transaction(t)
            print("Added transaction")
            return "reload"

        elif action == "mine":
            b.mine()
            return "reload"

        elif action == "verify_chain":
            return str(int(b.verify_chain()))
        
        elif action == "set_chain":
            ip = req["ip"]
            chain = get_chain(ip)
            b.chain = chain

        else:
            print(action)
            print(request.json)
    except Exception as ke:
        raise ke
        return str(1)


if __name__ == '__main__':
    """
    Run node on chosen port
    """
    app.run(port=int(port))
