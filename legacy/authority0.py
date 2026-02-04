# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from urllib.parse import urlparse
import rsa

# Part 1 - Building a Blockchain

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof=1, previous_hash='0')
        self.nodes = set()
        with open("Authority_0_PrivateKey.pem", 'rb') as f:
            self.private_key = rsa.PrivateKey.load_pkcs1(f.read())

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_authority(self):
        new_proof = rsa.sign(str(self.transactions).encode(),
                             self.private_key, 'SHA-256')
        new_proof = hashlib.sha256(str(new_proof).encode()).hexdigest()
        return str(new_proof)

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, uid, name, pid, court_id, district, section, state):
        self.transactions.append({'uid': uid,
                                  'name': name,
                                  'pid': pid,
                                  'court_id': court_id,
                                  'district': district,
                                  'section': section,
                                  'state': state
                                  })
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block

@app.route('/add_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    proof = blockchain.proof_of_authority()
    previous_hash = blockchain.hash(previous_block)

    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations,block mined! by (Authority0)',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': ' (Authority 0)- All good. The Blockchain is valid.'}
    else:
        response = {
            'message': '(Authority 0)-we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['uid', 'name', 'pid',
                        'court_id', 'district', 'section', 'state']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing in (Authority 0)', 400
    index = blockchain.add_transaction(
        json['uid'], json['name'], json['pid'], json['court_id'], json['district'], json['section'], json['state'])
    response = {
        'message': f'This transaction will be added to Block {index} by (Authority 0)'}
    return jsonify(response), 201

# Part 3 - Decentralizing our Blockchain

# Connecting new nodes
@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "Alert ! No node found. failed to connect (Authority 0)", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'Node Connection established! (Authority 0)',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'Chain updated in (Authority0) !!',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'The chain is the largest one (Authority0).',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200


@app.route('/verify_record', methods=['POST'])
def verify_record():
    json = request.get_json()
    uid = json.get('uid')

    for i in range(0, len(blockchain.chain)):
        block_transaction = blockchain.chain[i]["transactions"]

        for i in range(0, len(block_transaction)):
            transaction = block_transaction[i]["uid"]
            if str(transaction) == str(uid):
                response = {
                    "status": "Record Found",
                    "uid": block_transaction[i]["uid"],
                    "district": block_transaction[i]["district"],
                    "state": block_transaction[i]["state"],
                    "section": block_transaction[i]["section"],
                }
                return jsonify(response), 200
    return " The record was not found"


# Running the app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
