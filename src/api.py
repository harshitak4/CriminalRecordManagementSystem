from flask import Flask, jsonify, request
from src.blockchain import Blockchain

def create_app(node_id, port, peers=None):
    app = Flask(__name__)
    blockchain = Blockchain(node_id=node_id, data_file=f"data/chain_{node_id}.json")
    app.secret_key = f'super_secret_key_{node_id}' # Needed for flash messages
    
    if peers:
        for peer in peers:
            blockchain.add_node(peer)

    # Register UI Routes
    from src.web_routes import register_ui_routes
    register_ui_routes(app, blockchain)



    @app.route('/add_block', methods=['GET'])
    def mine_block():
        from src.crypto_utils import CryptoUtils
        previous_block = blockchain.get_previous_block()
        proof = blockchain.proof_of_authority()
        previous_hash = CryptoUtils.hash_block(previous_block)
        
        block = blockchain.create_block(proof, previous_hash)
        response = {
            'message': f'Block mined by Authority {node_id}',
            'index': block['index'],
            'timestamp': block['timestamp'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
            'transactions': block['transactions']
        }
        return jsonify(response), 200

    @app.route('/get_chain', methods=['GET'])
    def get_chain():
        response = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain)
        }
        return jsonify(response), 200

    @app.route('/is_valid', methods=['GET'])
    def is_valid():
        is_valid = blockchain.is_chain_valid(blockchain.chain)
        if is_valid:
            response = {'message': 'The Blockchain is valid.'}
        else:
            response = {'message': 'The Blockchain is not valid.'}
        return jsonify(response), 200

    @app.route('/add_transaction', methods=['POST'])
    def add_transaction():
        json_data = request.get_json()
        transaction_keys = ['uid', 'name', 'pid', 'court_id', 'district', 'section', 'state']
        if not all(key in json_data for key in transaction_keys):
            return 'Missing transaction elements', 400
        
        index = blockchain.add_transaction(json_data)
        response = {'message': f'Transaction added to Block {index}'}
        return jsonify(response), 201

    @app.route('/connect_node', methods=['POST'])
    def connect_node():
        json_data = request.get_json()
        nodes = json_data.get('nodes')
        if nodes is None:
            return "No node found", 400
        for node in nodes:
            blockchain.add_node(node)
        response = {
            'message': 'Node Connection established!',
            'total_nodes': list(blockchain.nodes)
        }
        return jsonify(response), 201

    @app.route('/replace_chain', methods=['GET'])
    def replace_chain():
        is_chain_replaced = blockchain.replace_chain()
        if is_chain_replaced:
            response = {'message': 'Chain updated', 'new_chain': blockchain.chain}
        else:
            response = {'message': 'Chain is already largest', 'actual_chain': blockchain.chain}
        return jsonify(response), 200

    @app.route('/verify_record', methods=['POST'])
    def verify_record():
        json_data = request.get_json()
        uid = json_data.get('uid')
        record = blockchain.verify_record(uid)
        if record:
            response = {
                "status": "Record Found",
                "data": record
            }
            return jsonify(response), 200
        return "Record not found", 404

    return app
