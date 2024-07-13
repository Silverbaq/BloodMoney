from ecdsa import SigningKey, SECP256k1
from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain
import sys

app = Flask(__name__)

#node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/mine', methods=['POST'])
def mine():
    values = request.get_json()

    required = ['wallet_address']
    if not all(k in values for k in required):
        return 'Missing wallet address', 400

    wallet_address = values['wallet_address']

    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender="0",
        recipient=wallet_address,
        amount=1,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

@app.route('/new_block', methods=['POST'])
def receive_new_block():
    values = request.get_json()

    required = ['index', 'timestamp', 'transactions', 'proof', 'previous_hash']
    if not all(k in values for k in required):
        return 'Missing values', 400

    last_block = blockchain.last_block
    if values['previous_hash'] != blockchain.hash(last_block):
        return 'Invalid block: Previous hash does not match', 400

    if not blockchain.valid_proof(last_block['proof'], values['proof']):
        return 'Invalid block: Proof of work is incorrect', 400

    block = {
        'index': values['index'],
        'timestamp': values['timestamp'],
        'transactions': values['transactions'],
        'proof': values['proof'],
        'previous_hash': values['previous_hash'],
    }

    blockchain.chain.append(block)
    return 'New block accepted', 200


from wallet import Wallet

# Create a new wallet
@app.route('/wallet/new', methods=['GET'])
def new_wallet():
    wallet = Wallet()
    response = {
        'private_key': wallet.private_key.to_string().hex(),
        'public_key': wallet.public_key.to_string().hex(),
        'address': wallet.get_address()
    }
    return jsonify(response), 200

# Check wallet balance
@app.route('/wallet/balance/<address>', methods=['GET'])
def wallet_balance(address):
    balance = blockchain.get_balance(address)
    response = {
        'address': address,
        'balance': balance
    }
    return jsonify(response), 200

# Create a new transaction
@app.route('/wallet/transaction', methods=['POST'])
def create_transaction():
    values = request.get_json()

    required = ['sender_private_key', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    sender_wallet = Wallet()
    sender_wallet.private_key = SigningKey.from_string(bytes.fromhex(values['sender_private_key']), curve=SECP256k1)
    sender_wallet.public_key = sender_wallet.private_key.get_verifying_key()

    transaction, signature = sender_wallet.create_transaction(values['recipient'], values['amount'])
    transaction['signature'] = signature

    index = blockchain.new_transaction(transaction['sender'], transaction['recipient'], transaction['amount'], transaction['signature'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


if __name__ == '__main__':
    port = int(sys.argv[1])
    bootstrap_node = sys.argv[2] if len(sys.argv) > 2 else None
    blockchain.port = port
    if bootstrap_node:
        blockchain.bootstrap_network(bootstrap_node)
    blockchain.start_periodic_resolution()

    app.run(host='0.0.0.0', port=port)
