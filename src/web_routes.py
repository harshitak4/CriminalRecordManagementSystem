from flask import Blueprint, render_template, request, redirect, flash, url_for
import requests

def register_ui_routes(app, blockchain):
    @app.route('/')
    def dashboard():
        return render_template('index.html', 
                               chain=blockchain.chain, 
                               pending_tx_count=len(blockchain.transactions),
                               peers_count=len(blockchain.nodes),
                               node_id=blockchain.node_id)

    @app.route('/add_record', methods=['GET', 'POST'])
    def add_record_page():
        if request.method == 'POST':
            data = {
                'uid': request.form['uid'],
                'name': request.form['name'],
                'pid': request.form['pid'],
                'court_id': request.form['court_id'],
                'district': request.form['district'],
                'section': request.form['section'],
                'state': request.form['state']
            }
            blockchain.add_transaction(data)
            flash('Transaction added successfully! Mine a block to confirm it.', 'success')
            return redirect(url_for('dashboard'))
        return render_template('add_record.html', node_id=blockchain.node_id)

    @app.route('/verify', methods=['GET', 'POST'])
    def verify_page():
        result = None
        searched = False
        searched_uid = None
        
        if request.method == 'POST':
            searched = True
            searched_uid = request.form['uid']
            result = blockchain.verify_record(searched_uid)
            
        return render_template('verify.html', 
                               result=result, 
                               searched=searched, 
                               searched_uid=searched_uid,
                               node_id=blockchain.node_id)

    @app.route('/mine', methods=['GET'])
    def mine_page():
        from src.crypto_utils import CryptoUtils
        
        if not blockchain.transactions:
            flash('No transactions to mine.', 'error')
            return redirect(url_for('dashboard'))

        previous_block = blockchain.get_previous_block()
        proof = blockchain.proof_of_authority()
        previous_hash = CryptoUtils.hash_block(previous_block)
        
        blockchain.create_block(proof, previous_hash)
        flash('Block mined successfully!', 'success')
        return redirect(url_for('dashboard'))

    @app.route('/sync', methods=['GET'])
    def sync_page():
        replaced = blockchain.replace_chain()
        if replaced:
            flash('Chain verified and updated from peers.', 'success')
        else:
            flash('Chain is already up to date.', 'success')
        return redirect(url_for('dashboard'))
