from flask import Flask, request, jsonify, render_template
from time import time
from flask_cors import CORS
from collections import OrderedDict
import binascii
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA

MINING_SENDER = "The Blockchain"
class Blockchain:
    def __init__(self):
        self.transactions = []
        self.chain = []
        self.create_block(0, '00')

    def create_block(self, nonce, previous_hash):
        block = {'block_number': len(self.chain) + 1,
                 'timestamp': time(),
                 'transactions': self.transactions,
                 'nonce': nonce,
                 'previous_hash': previous_hash

                 }
        # reset list of transaction
        self.transactions = []
        self.chain.append(block)

    def verify_transaction_signature(self, sender_public_key, signature, transaction):
        public_key = RSA.importKey(binascii.unhexlify(sender_public_key))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        try:
            verifier.verify(h, binascii.unhexlify(signature))
            return True

        except ValueError:
            return False

    def submit_transaction(self, sender_public_key, recipient_public_key, signature, amount):
        # TODO: Reward the miner

        transaction = OrderedDict({
            'sender_public_key': sender_public_key,
            'recipient_public_key': recipient_public_key,
            'amount': amount
        })
        # reward for mining
        if sender_public_key == MINING_SENDER:
            self.transactions.append(transaction)
            return len(self.chain) + 1
        else:
            # normal transaction
            signature_verification = self.verify_transaction_signature(sender_public_key, signature, transaction)
            if signature_verification:
                self.transactions.append(transaction)
                return len(self.chain) + 1
            else:
                return False


blockchain = Blockchain()

app = Flask(__name__)
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form
    # check the required field
    required = ['confirmation_sender_public_key', 'confirmation_recipient_public_key', 'transaction_signature', 'confirmation_amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    transaction_results = blockchain.submit_transaction(values['confirmation_sender_public_key'],
                                                        values['confirmation_recipient_public_key'],
                                                        values['transaction_signature'], values['confirmation_amount'])
    if not transaction_results:
        response = {'message': 'Invalid transaction'}
        return jsonify(response), 406
    else:
        response = {'message': 'transaction will be added to the Block ' + str(transaction_results)}

    return jsonify(response), 201


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5001, type=int, help="port to listen to")
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port, debug=True)
