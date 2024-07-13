import hashlib
import json
from time import time
from uuid import uuid4
from urllib.parse import urlparse
import requests
import threading

from wallet import Wallet


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.port = None  # This will be set later

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            try:
                response = requests.get(f'http://{node}/chain')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']

                    if length > max_length and self.valid_chain(chain):
                        max_length = length
                        new_chain = chain
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to node {node}: {e}")

        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        self.broadcast_new_block(block)
        self.trigger_resolve()  # Trigger resolution on other nodes
        return block



    def new_transaction(self, sender, recipient, amount, signature=None):
        if sender != "0":  # Skip verification for mining rewards
            wallet = Wallet()
            if not wallet.verify_transaction({'sender': sender, 'recipient': recipient, 'amount': amount}, signature, sender):
                return 'Invalid transaction signature', 400

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['recipient'] == address:
                    balance += int(transaction['amount'])
                if transaction['sender'] == address:
                    balance -= int(transaction['amount'])
        return balance

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def broadcast_new_block(self, block):
        neighbours = self.nodes
        for node in neighbours:
            try:
                response = requests.post(f'http://{node}/new_block', json=block)
                if response.status_code != 200:
                    print(f"Failed to broadcast to node {node}")
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to node {node}: {e}")

    def trigger_resolve(self):
        neighbours = self.nodes
        for node in neighbours:
            try:
                requests.get(f'http://{node}/nodes/resolve')
            except requests.exceptions.RequestException as e:
                print(f"Error connecting to node {node}: {e}")

    def bootstrap_network(self, bootstrap_node):
        try:
            self.register_node(bootstrap_node)
            bootstrap_node_netloc = urlparse(bootstrap_node).netloc
            requests.post(f'http://{bootstrap_node_netloc}/nodes/register', json={'nodes': [f'http://127.0.0.1:{self.port}']})
            self.resolve_conflicts()
        except requests.exceptions.RequestException as e:
            print(f"Error during bootstrap: {e}")

    def start_periodic_resolution(self, interval=30):  # Reduced interval
        def resolve_periodically():
            self.resolve_conflicts()
            threading.Timer(interval, resolve_periodically).start()

        resolve_periodically()
