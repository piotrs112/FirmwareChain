import json
import sys

from flask import (Flask, render_template, request)
from cryptography.hazmat.backends.openssl.rsa import (_RSAPrivateKey
                                                     , _RSAPublicKey)   

from blockchain import Blockchain
from transaction import Transaction

app = Flask(__name__, template_folder="interface", static_folder="interface")
b = Blockchain()


@app.route('/', methods=['GET'])
def index():
    """
    Returns index page
    """

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
                if type(v) is _RSAPublicKey:
                    if t.is_signed:
                        signed = "Signed"
                    else: signed = "Not signed"
                    line.append(signed)
                elif type(v) is bytes:
                    line.append(hash(v))
                else:
                    line.append(v)
            p_t.append(line)
    else:
        t_h = []
        p_t = []

    return render_template("index.html",
                           blocks=data,
                           head=head,
                           transactions_head=t_h,
                           pending_transactions=p_t)


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

    return json.dumps({"blocks":str(data),
                        "head":str(head),
                        "transactions_head": t_h,
                        "pending_transactions": p_t})


@app.route('/rest/', methods=['POST'])
def rest_api():
    """
    REST API for interacting with node
    """

    print("Connection omg")
    try:
        action = request.json['action']
        print(action)
        req = request.json
        if action == "get_chain":
            # todo: make Block serializable
            return str(len(b.chain))
        elif action == "add_transaction":
            data = req["transaction"]
            t = Transaction(
                b.public_key, data['version'], data['file_hash'], data['filename'])
            t.sign(b.private_key)
            b.add_transaction(t)
            print("Added transaction")
            return str(0)
        elif action == "mine":
            b.mine()
            return str(0)
        elif action == "verify_chain":
            return json.dumps(b.verify_chain())
        else:
            print(action)
            print(request.json)
    except Exception as ke:
        raise ke
    finally:
        return index()


if __name__ == '__main__':
    """
    Run node on chosen port
    """

    if len(sys.argv) == 1:
        port = 5000
    else:
        port = sys.argv[-1]
    app.run(port=port)
