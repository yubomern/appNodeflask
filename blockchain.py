import hashlib
import datetime
import json
import requests
import secrets
from urllib.parse import urlparse
from flask import Flask, jsonify, request

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hashlib.sha256((str(self.index) + str(self.timestamp) + str(self.transactions) + str(self.previous_hash) + str(self.nonce)).encode()).hexdigest()

    def mine_block(self, difficulty):
        while self.hash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print("Block mined:", self.hash)

class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def to_dict(self):
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount
        }

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4
        self.pending_transactions = []
        self.mining_reward = 100
        self.token = MessdakToken()
        self.nodes = set()

    def create_genesis_block(self):
        return Block(0, datetime.datetime.now(), [], "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.mine_block(self.difficulty)
        print("Block successfully mined!")
        self.chain.append(new_block)
        self.pending_transactions = []

    def create_transaction(self, transaction):
        self.pending_transactions.append(transaction)
        return self.get_latest_block().index + 1

    def mine_pending_transactions(self, miner):
        reward_transaction = Transaction(None, miner, self.mining_reward)
        self.pending_transactions.append(reward_transaction)
        new_block = Block(len(self.chain), datetime.datetime.now(), self.pending_transactions, self.get_latest_block().hash)
        self.add_block(new_block)
        self.token.create_transaction(None, miner, self.mining_reward)  # Récompense minière en Messdak tokens
        return new_block

    def validate_transactions(self):
        for transaction in self.pending_transactions:
            if not self.token.create_transaction(transaction.sender, transaction.receiver, transaction.amount):
                return False
        return True

    def get_balance(self, address):
        return self.token.get_balance(address)

    def is_chain_valid(self, chain=None):
        if chain is None:
            chain = self.chain
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

            if not self.is_valid_proof(current_block, self.difficulty):
                return False

        return True

    def is_valid_proof(self, block, difficulty):
        return block.hash[:difficulty] == "0" * difficulty

    def print_chain(self):
        for block in self.chain:
            print(json.dumps(block.__dict__, default=str, indent=4))  # Convertit la date en chaîne de caractères

    def add_node(self, node_url):
        parsed_url = urlparse(node_url)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)

        for node in network:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True

        return False

    def resolve_conflicts(self):
        replaced = self.replace_chain()

        if replaced:
            self.pending_transactions = []
            return True

        return False

class MessdakToken:
    def __init__(self):
        self.total_supply = 1000000  # Offre totale de jetons Messdak
        self.balance = {}  # Dictionnaire pour stocker les soldes des adresses

    def create_transaction(self, sender, receiver, amount):
        if sender not in self.balance:
            self.balance[sender] = self.total_supply
        if receiver not in self.balance:
            self.balance[receiver] = 0

        if self.balance[sender] >= amount:
            self.balance[sender] -= amount
            self.balance[receiver] += amount
            return True
        else:
            return False

    def get_balance(self, address):
        if address in self.balance:
            return self.balance[address]
        else:
            return 0

# Initialisation de l'application Flask
app = Flask(__name__)

# Initialisation de la blockchain
blockchain = Blockchain()

class Wallet:
    def __init__(self):
        self.private_key = secrets.token_hex(32)  # Génère une clé privée aléatoire
        self.public_key = hashlib.sha256(self.private_key.encode()).hexdigest()  # Calcule la clé publique à partir de la clé privée

    def get_balance(self):
        return blockchain.get_balance(self.public_key)

# Endpoint pour ajouter une transaction à la blockchain
@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Vérifier que les champs requis sont présents dans la requête
    required_fields = ['sender', 'receiver', 'amount']
    if not all(field in values for field in required_fields):
        return 'Missing values', 400

    # Créer une nouvelle transaction
    index = blockchain.create_transaction(Transaction(values['sender'], values['receiver'], values['amount']))

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

# Endpoint pour miner un nouveau bloc
@app.route('/mine', methods=['GET'])
def mine():
    # Miner les transactions en attente
    new_block = blockchain.mine_pending_transactions("miner_address")

    response = {
        'message': 'New Block Mined',
        'index': new_block.index,
        'transactions': [transaction.to_dict() for transaction in new_block.transactions],
        'nonce': new_block.nonce,
        'previous_hash': new_block.previous_hash,
        'hash': new_block.hash
    }
    return jsonify(response), 200

# Endpoint pour consulter la chaîne de la blockchain
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': [],
        'length': len(blockchain.chain)
    }

    for block in blockchain.chain:
        transactions = []
        for transaction in block.transactions:
            transactions.append(transaction.to_dict())
        block_data = {
            'index': block.index,
            'timestamp': str(block.timestamp),
            'transactions': transactions,
            'nonce': block.nonce,
            'previous_hash': block.previous_hash,
            'hash': block.hash
        }
        response['chain'].append(block_data)

    return jsonify(response), 200

# Endpoint pour résoudre les conflits entre les nœuds
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': []
        }
        for block in blockchain.chain:
            transactions = []
            for transaction in block.transactions:
                transactions.append(transaction.to_dict())
            block_data = {
                'index': block.index,
                'timestamp': str(block.timestamp),
                'transactions': transactions,
                'nonce': block.nonce,
                'previous_hash': block.previous_hash,
                'hash': block.hash
            }
            response['new_chain'].append(block_data)
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': []
        }
        for block in blockchain.chain:
            transactions = []
            for transaction in block.transactions:
                transactions.append(transaction.to_dict())
            block_data = {
                'index': block.index,
                'timestamp': str(block.timestamp),
                'transactions': transactions,
                'nonce': block.nonce,
                'previous_hash': block.previous_hash,
                'hash': block.hash
            }
            response['chain'].append(block_data)

    return jsonify(response), 200

# Endpoint pour consulter le solde d'un compte Messdak
@app.route('/balance', methods=['GET'])
def get_balance():
    address = request.args.get('address')
    balance = blockchain.get_balance(address)
    response = {'address': address, 'balance': balance}
    return jsonify(response), 200

# Endpoint pour créer un nouveau portefeuille
@app.route('/wallet/new', methods=['GET'])
def create_wallet():
    new_wallet = Wallet()
    response = {'public_key': new_wallet.public_key}
    return jsonify(response), 200

# Endpoint pour consulter le solde d'un portefeuille
@app.route('/wallet/balance', methods=['GET'])
def get_wallet_balance():
    public_key = request.args.get('public_key')
    balance = blockchain.get_balance(public_key)
    response = {'public_key': public_key, 'balance': balance}
    return jsonify(response), 200

# Démarrer l'application Flask sur le port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)