import hashlib
import json
from time import time
from uuid import uuid4
from collections import OrderedDict

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        self.new_block(previous_hash=1, proof=2)

    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        print(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: <str> Address of the Recipient
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the BLock that will hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        # hashlib.sha3_256()
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, last_proof):

        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1

        # for block 1 hash (1, p) = 000000xx
        """
        Simple Proof of Work Algorithm
        Find a number p such that hash(last_block_string, p) contains 6 leading
        zeroes
        """

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f"{last_proof}{proof}".encode()
        hash_guess = hashlib.sha3_256(guess).hexdigest()
        check = hash_guess[0:4]
        # print(hash_guess)
        if check == '000':
            return True
        else:
            return False
        # """
        # Validates the Proof:  Does hash(block_string, proof) contain 6
        # leading zeroes?
        # """
        # TODO
        pass

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-------------------\n")
            # Check that the hash of the block is correct
            if block.previous_hash is not self.hash(chain[current_index - 1]):
                return False
            elif not self.valid_proof(block.previous_hash, self.hash(block)):
                return False
            else:
                return True
            last_block = block
            current_index += 1

        return True


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

print(blockchain.valid_chain(blockchain.chain))

@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    proof = blockchain.proof_of_work(blockchain.last_block)

    # We must receive a reward for finding the proof.
    blockchain.new_transaction("0", node_identifier, 1)

    block = blockchain.new_block(proof, blockchain.hash(blockchain.last_block))
    # TODO:
    # The sender is "0" to signify that this node has mine a new coin
    # The recipient is the current node, it did the mining!
    # The amount is 1 coin as a reward for mining the next block

    # Forge the new Block by adding it to the chain
    # TODO

    # Send a response with the new block
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    print(response)
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing Values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'],
                                       values['recipient'],
                                       values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
        'current_Chain': blockchain.chain
        # TODO: Return the chain and its current length
    }

    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
