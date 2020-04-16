import json
import sys

from flask import Flask

from blockchain import Blockchain

app = Flask(__name__)
b = Blockchain()

@app.route('/', methods=['GET'])
def index() -> str:
    """
    Returns index page
    """

    html = ""
    for block in b.chain:
        html += str(block)
        html += "\n"
    return html

if __name__ == '__main__':
    """
    Run node on chosen port
    """
    
    if len(sys.argv) == 1:
       port = 5000
    else:
       port = sys.argv[-1]
    app.run(port=port)
