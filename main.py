import hashlib
import json
from time import time


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
            'timestamp': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Resets the current list of transactrions
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

        return self.last_block['index]'] + 1

    def proof_of_work(self, last_proof):
        # This is the proof of work algorithm, which in short,
        # should be result in values difficult to compute yet easy to verify.
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

    def hash(block):
        # creates a SHA-256 hash of a block
        # the creation of this dictionary must be ordered to provide consistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    @property
    def last_block(self):
        # returns the last Block in the chain
        return self.chain[-1]

