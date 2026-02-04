import datetime
import json
import requests
from urllib.parse import urlparse
from src.crypto_utils import CryptoUtils

class Blockchain:
    def __init__(self, node_id, key_dir="keys", data_file="data/chain.json"):
        self.chain = []
        self.transactions = []
        self.nodes = set()
        self.node_id = node_id
        self.public_key, self.private_key = CryptoUtils.load_keys(node_id, key_dir)
        self.data_file = data_file
        self.load_chain()
        
        if not self.chain:
            self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': self.transactions,
            'validator': self.node_id
        }
        self.transactions = []
        self.chain.append(block)
        self.save_chain()
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_authority(self):
        return CryptoUtils.sign_data(self.transactions, self.private_key)

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != CryptoUtils.hash_block(previous_block):
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, transaction_data):
        self.transactions.append(transaction_data)
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
            try:
                response = requests.get(f'http://{node}/get_chain')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']
                    if length > max_length and self.is_chain_valid(chain):
                        max_length = length
                        longest_chain = chain
            except requests.RequestException:
                continue
                
        if longest_chain:
            self.chain = longest_chain
            self.save_chain()
            return True
        return False

    def save_chain(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.chain, f, indent=4)
        except Exception:
            pass

    def load_chain(self):
        try:
            with open(self.data_file, 'r') as f:
                self.chain = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.chain = []

    def verify_record(self, uid):
        for block in self.chain:
            for transaction in block.get("transactions", []):
                if str(transaction.get("uid")) == str(uid):
                    return transaction
        return None
