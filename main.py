import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Creation of the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        # creates a new Block to be added to the chain

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        # Why store the previous hash? As Mr. Nakamoto proposed, it's how we replace trust in a P2P system.
        # In other words, the corruption of the previous block breaks the chain- breaking validity.

        # Resets the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        # Creates a new transaction to go into the next mined Block
        """
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Reecipient
        :param amount: <int> Amount
        :return: <int> The index of the Block that will hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        # This is the proof of work algorithm, which in short,
        # should result in values difficult to compute yet easy to verify.
        # Notes for self: Bitcoin's POW references Adam Back's "Hashcash"
        """
        For the purpose of this function, the Proof of Work algorithm will be:
        - Find a number p such that hash(Pp) contains 4 leading zeroes, where P is the previous p
        :param last_proof: <int>
        :return: <int>
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof = proof + 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        The purpose of this static function is to validate the proof. Essentially asking,
        does  hash(last_proof, proof) contain 4 leading zeroes?
        :param last_proof: <int> previous proof
        :param proof: <int> current proof
        :return: <boolean value> True if correct, False if not
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        # creates a SHA-256 hash of a block
        # the creation of this dictionary must be ordered to provide consistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    @property
    def last_block(self):
        # returns the last Block in the chain
        return self.chain[-1]


# Instantiation of the node
app = Flask(__name__)

# generating a unique address
node_identifier = str(uuid4()).replace('-', '')

# instantiation of the blockchain
blockchain = Blockchain()


# this creates a mine endpoint, a get request to mine for a new block
@app.route('/mine', methods=["GET"])
def mine():
    # begins by running the proof of work algorithm to get the next proof
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Reward (coin) sent for finding a proof.
    # The sender is demarked as 0 to signify that this node has mined a new coin

    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1
    )

    # Crafting new block and adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


# A POST request creates a new transaction because we are sending data
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # We necessitate the user to send certain values in the POST data
    required_fields = ['sender', 'recipient', 'amount']

    # generator iterating over each requirment and chcecking if all are there
    if not all (v in values for v in required_fields):
        return 'Missing required values', 400

    # creation of a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201


# returns the full blockchain
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


# runs the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

