import blockchain
import transactions
from blocks import Block
import hashlib
import time
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
import json
from transactions import Transactions
from blockchain import BlockChain
from person import get_random_people
import random
import os
import keys



class P2PNetwork:
    def __init__(self):
        self.nodes = []
        self.mempool = []

    def add_node(self, node):
        self.nodes.append(node)

    def broadcast_transaction(self, transaction):
        for node in self.nodes:
            node.receive_transaction(transaction)

    def broadcast_block(self, block):
        for node in self.nodes:
            node.receive_block(block)



class FullNode:
    def __init__(self, key_id, key_folder):
        self.privkey_file = os.path.join(key_folder, f'private_key_full_{key_id}.pem')
        self.pubkey_file = os.path.join(key_folder, f'public_key_full_{key_id}.pem')
        keys.generate_private_key(self.privkey_file)
        keys.generate_public_key(self.privkey_file, self.pubkey_file)
        self.blockchain = BlockChain()
        self.mempool = []


    def create_transaction(self, receiver_pubkey_file, data):
        encrypted_data = keys.encrypt_transaction(receiver_pubkey_file, data)
        signature = keys.generate_signiture(self.privkey_file, encrypted_data)
        return Transactions(self.pubkey_file, receiver_pubkey_file, signature, encrypted_data)
    def receive_transaction(self, transaction):
        if transaction.verify_signature():
            self.mempool.append(transaction)
        else:
            print("Invalid transaction signature")

    def mine_block(self):
        if len(self.mempool) == 0:
            print("No transactions in mempool")
            return

        previous_hash = self.blockchain.chain[-1].hash
        new_block = Block(len(self.blockchain.chain), self.mempool, previous_hash, time.time(), 0)
        new_block.mine(self.blockchain.difficulty)
        self.blockchain.chain.append(new_block)
        self.mempool.clear()

    def receive_block(self, block):
        if self.blockchain.is_chain_valid():
            self.blockchain.chain.append(block)

class LightNode:
    def __init__(self, key_id, key_folder):
        self.privkey_file = os.path.join(key_folder, f'private_key_light_{key_id}.pem')
        self.pubkey_file = os.path.join(key_folder, f'public_key_light_{key_id}.pem')
        keys.generate_private_key(self.privkey_file)
        keys.generate_public_key(self.privkey_file, self.pubkey_file)

    def create_transaction(self, receiver_pubkey_file, data):
        encrypted_data = keys.encrypt_transaction(receiver_pubkey_file, data)
        signature = keys.generate_signiture(self.privkey_file, encrypted_data)
        return Transactions(self.pubkey_file, receiver_pubkey_file, signature, encrypted_data)

    def send_transaction(self, transaction, network):
        for node in network.nodes:
            if isinstance(node, FullNode):
                node.receive_transaction(transaction)

def main():
    network = P2PNetwork()
    num_full_nodes = 5
    num_light_nodes = 10
    num_transactions = 20
    key_folder = "keys"

    # Create the folder if it doesn't exist
    if not os.path.exists(key_folder):
        os.makedirs(key_folder)

    # Creating and adding nodes to the network
    for i in range(num_full_nodes):
        full_node = FullNode(i, key_folder)
        network.add_node(full_node)

    for i in range(num_light_nodes):
        light_node = LightNode(i, key_folder)
        network.add_node(light_node)

    # Randomly pick a light node to transact and a full node to mine
    people = get_random_people()
    for _ in range(num_transactions):
        light_node = random.choice([n for n in network.nodes if isinstance(n, LightNode)])
        receiver_node = random.choice([n for n in network.nodes if isinstance(n, LightNode) and n != light_node])
        person_data = random.choice(people)
        person_data_json = json.dumps(person_data.__dict__)

        transaction = light_node.create_transaction(receiver_node.pubkey_file, person_data_json)
        light_node.send_transaction(transaction, network)

        full_node = random.choice([n for n in network.nodes if isinstance(n, FullNode)])
        full_node.mine_block()
        new_block = full_node.blockchain.chain[-1]
        network.broadcast_block(new_block)

    # Print blockchain for all full nodes
    for i, node in enumerate([n for n in network.nodes if isinstance(n, FullNode)]):
        print(f"Blockchain for FullNode{i + 1}:")
        for block in node.blockchain.chain:
            print(f"  Block {block.index}: {block.hash}")

if __name__ == "__main__":
    main()
