from blocks import Block
import time
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes
import json
from blockchain import BlockChain
from person import get_random_people
import random
import os
import keys
import pickle
import queue
import threading




class P2PNetwork:
    def __init__(self):
        self.nodes = []
        self.lightnodes = []
        self.mempool = []

    def add_node(self, node):
        if isinstance(node, FullNode):
            self.nodes.append(node)
        elif isinstance(node, LightNode):
            self.lightnodes.append(node)

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
        transaction = keys.generate_transaction(self.privkey_file, self.pubkey_file, data, receiver_pubkey_file)
        return transaction
    def receive_transaction(self, transaction):
        if transaction.verify_signature():
            self.mempool.append(transaction)
        else:
            print("Invalid transaction signature")

    def mine_block(self):
        if len(self.mempool) == 0:
            print("No transactions in mempool")
            return

        # Select at most 2 transactions from the mempool
        transactions_to_mine = self.mempool[:2]

        self.blockchain.addBlock(transactions_to_mine)

        # Remove the mined transactions from the mempool
        self.mempool = self.mempool[2:]

    def receive_block(self, block):
        if self.blockchain.is_chain_valid():
            self.blockchain.blocks.append(block)
            self.blockchain.blockchain_size += 1

class LightNode:
    def __init__(self, key_id, key_folder):
        self.privkey_file = os.path.join(key_folder, f'private_key_light_{key_id}.pem')
        self.pubkey_file = os.path.join(key_folder, f'public_key_light_{key_id}.pem')
        keys.generate_private_key(self.privkey_file)
        keys.generate_public_key(self.privkey_file, self.pubkey_file)

    def create_transaction(self, receiver_pubkey_file, data):
        transaction = keys.generate_transaction(self.privkey_file, self.pubkey_file, data, receiver_pubkey_file)
        return transaction


    def send_transaction(self, transaction, network):
        for node in network.nodes:
            if isinstance(node, FullNode):
                node.receive_transaction(transaction)


def save_blockchain(blockchain, filename='blockchain.pickle'):
    with open(filename, 'wb') as handle:
        pickle.dump(blockchain, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_blockchain(filename='blockchain.pickle'):
    with open(filename, 'rb') as handle:
        return pickle.load(handle)

class UserNode(LightNode):
    pass

def add_user_node(network, key_id, key_folder):
    user_node = UserNode(key_id, key_folder)
    network.add_node(user_node)
    return user_node

def simulate(network, key_folder, new_nodes_queue):
    people = get_random_people()

    while True:
        # Check for new nodes in the queue
        while not new_nodes_queue.empty():
            new_node = new_nodes_queue.get()
            network.add_node(new_node)

        num_transactions = random.randint(1, 5)  # Random number of transactions per iteration
        for _ in range(num_transactions):
            time.sleep(1)  # Sleep for 1 second between transactions

            light_node = random.choice(network.lightnodes)
            receiver_node = random.choice([n for n in network.lightnodes if n != light_node])

            person_data = random.choice(people)
            person_data_json = json.dumps(person_data.__dict__)

            transaction = light_node.create_transaction(receiver_node.pubkey_file, person_data_json)
            light_node.send_transaction(transaction, network)

            full_node = random.choice([n for n in network.nodes if isinstance(n, FullNode)])

            full_node.mine_block()
            new_block = full_node.blockchain.blocks[-1]
            network.broadcast_block(new_block)

            # Save the blockchain
            save_blockchain(full_node.blockchain)

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

    # Load the existing blockchain if it exists
    try:
        blockchain = load_blockchain()
        for node in network.nodes:
            if isinstance(node, FullNode):
                node.blockchain = blockchain
    except FileNotFoundError:
        pass


    new_nodes_queue = queue.Queue()

    # Start the simulation in a separate thread
    simulation_thread = threading.Thread(target=simulate, args=(network, key_folder, new_nodes_queue))
    simulation_thread.daemon = True  # Set the thread as a daemon to terminate with the main program
    simulation_thread.start()

    while True:
        time.sleep(5)  # Add a new user node every 5 seconds (for demonstration purposes)
        key_id = len(network.lightnodes)
        user_node = add_user_node(network, key_id, key_folder)
        new_nodes_queue.put(user_node)

    # Print blockchain for all full nodes
    for i, node in enumerate([n for n in network.nodes if isinstance(n, FullNode)]):
        print(f"Blockchain for FullNode{i + 1}:")
        for block in node.blockchain.blocks:
            print(f"  Block {block.block_number}:")
            print(f"Transactions {block.transactions}")
            for i in block.transactions:
                print(f"Sender: {i.sender_public_key} \n Receiver: {i.receiver_public_key} \n transaction data: encrypted")
            print(f"Timestamp: {block.timestamp} \n previous_hash: {block.previous_hash} \n hash: {block.hash}")

if __name__ == "__main__":
    main()