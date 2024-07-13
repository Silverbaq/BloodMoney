import binascii
from ecdsa import SigningKey, SECP256k1, VerifyingKey
import json

class Wallet:
    def __init__(self):
        self.private_key = self.generate_private_key()
        self.public_key = self.generate_public_key(self.private_key)

    @staticmethod
    def generate_private_key():
        return SigningKey.generate(curve=SECP256k1)

    @staticmethod
    def generate_public_key(private_key):
        return private_key.get_verifying_key()

    def sign_transaction(self, transaction):
        transaction_data = json.dumps(transaction, sort_keys=True).encode()
        return binascii.hexlify(self.private_key.sign(transaction_data)).decode()

    @staticmethod
    def verify_transaction(transaction, signature, public_key):
        transaction_data = json.dumps(transaction, sort_keys=True).encode()
        public_key = VerifyingKey.from_string(binascii.unhexlify(public_key), curve=SECP256k1)
        return public_key.verify(binascii.unhexlify(signature), transaction_data)

    def get_address(self):
        return binascii.hexlify(self.public_key.to_string()).decode()

    def check_balance(self, blockchain):
        balance = 0
        address = self.get_address()
        for block in blockchain.chain:
            for transaction in block['transactions']:
                if transaction['recipient'] == address:
                    balance += transaction['amount']
                if transaction['sender'] == address:
                    balance -= transaction['amount']
        return balance

    def create_transaction(self, recipient, amount):
        transaction = {
            'sender': self.get_address(),
            'recipient': recipient,
            'amount': amount,
        }
        signature = self.sign_transaction(transaction)
        return transaction, signature