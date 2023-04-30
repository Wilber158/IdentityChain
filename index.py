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
import eel
import tkinter as tk
from tkinter import filedialog
import faker
import datetime
import os



class P2PNetwork:
    def __init__(self):
        self.nodes = []
        self.lightnodes = []
        self.userNodes = []
        self.mempool = []

    def add_node(self, node):
        if isinstance(node, FullNode):
            self.nodes.append(node)
        elif isinstance(node, LightNode):
            self.lightnodes.append(node)
        elif isinstance(node, UserNode):
            self.userNodes.append(node)

    def broadcast_transaction(self, transaction):
        for node in self.nodes:
            node.receive_transaction(transaction)

    def broadcast_block(self, block, blockchain_size):
        for node in self.nodes:
            node.receive_block(block, blockchain_size)




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

    def receive_block(self, block, blockchain_size):
        # If the block is received from another node with a longer blockchain, update the local blockchain
        if blockchain_size > self.blockchain.blockchain_size:
            # Append the block to the local blockchain only if it is valid
            temp_blockchain = self.blockchain.blocks.copy()
            temp_blockchain.append(block)
            temp_blockchain_instance = BlockChain()
            temp_blockchain_instance.blocks = temp_blockchain
            temp_blockchain_instance.blockchain_size = len(temp_blockchain)
            
            if temp_blockchain_instance.is_chain_valid():
                self.blockchain = temp_blockchain_instance


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
    def __init__(self, priv_key, pub_key):
        self.privkey_file = priv_key
        self.pubkey_file = pub_key
        pass


def serialize_person_data(person_data):
    def convert(o):
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        raise TypeError(f'Object of type {type(o).__name__} is not JSON serializable')

    return json.dumps(person_data.__dict__, default=convert)

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
            time.sleep(30)  # Sleep for 1 second between transactions

            light_node = random.choice(network.lightnodes)
            receiver_node = random.choice([n for n in network.lightnodes if n != light_node])

            person_data = random.choice(people)
            person_data_json = serialize_person_data(person_data)

            print(f"Person data: {person_data_json}")  # Debug print
            
            transaction = light_node.create_transaction(receiver_node.pubkey_file, person_data_json)

            print(f"Transaction: {transaction}")  # Debug print

            light_node.send_transaction(transaction, network)

            full_node = random.choice([n for n in network.nodes if isinstance(n, FullNode)])

            full_node.mine_block()
            new_block = full_node.blockchain.blocks[-1]
            network.broadcast_block(new_block, full_node.blockchain.blockchain_size)  # Send the size

            # Save the blockchain
            save_blockchain(full_node.blockchain)



network = P2PNetwork()
@eel.expose
def get_blockchain_data():
    full_node = [n for n in network.nodes if isinstance(n, FullNode)][0]
    blockchain_data = []

    for block in full_node.blockchain.blocks:
        transactions_data = [transaction.__dict__ for transaction in block.transactions]
        block_data = {
            'block_number': block.block_number,
            'transactions': transactions_data,
            'timestamp': block.timestamp,
            'previous_hash': block.previous_hash,
            'hash': block.hash
        }
        blockchain_data.append(block_data)

    return blockchain_data


@eel.expose
def select_directory():
    root = tk.Tk()
    root.withdraw()  # hide the main window

    # open a dialog box to select a directory
    selected_directory = filedialog.askdirectory()

    # store the selected directory as a string
    selected_directory_str = str(selected_directory)

    return selected_directory_str


network = P2PNetwork()

def main():
    print("Happening")
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
        time.sleep(20)  # Add a new user node every 5 seconds (for demonstration purposes)
        key_id = len(network.lightnodes)
        user_node = add_user_node(network, key_id, key_folder)
        new_nodes_queue.put(user_node)

        # Print blockchain for all full nodes
        for i, node in enumerate([n for n in network.nodes if isinstance(n, FullNode)]):
            print(f"Blockchain for FullNode{i + 1}:")
            for block in node.blockchain.blocks:
                print(f"  Block {block.block_number}:")
                
                # Loop through the transactions in the block
                for transaction in block.transactions:
                    print(f"    Transaction:")
                    print(f"      Sender Public Key: {transaction.sender_public_key}")
                    print(f"      Receiver Public Key: {transaction.receiver_public_key}")
                    print(f"Transaction contents: {transaction.transaction_data}")
                
                print(f"Timestamp: {block.timestamp} \n previous_hash: {block.previous_hash} \n hash: {block.hash}")

@eel.expose
def create_user_node(seed, file_name, file_dir):
    priv_dir = f"{file_dir}/{file_name}.pem"
    pub_dir = f"{file_dir}/{file_name}_pub.pem"
    print(priv_dir)
    print(pub_dir)
    print(f"{seed} type: {type(seed)}")
    keys.generate_Mnemonic_private_key(seed, priv_dir)
    keys.generate_user_key(priv_dir, pub_dir, file_dir)
    node = UserNode(priv_dir, pub_dir)
    network.add_node(node)




def run_main_in_thread():
    main()


if __name__ == "__main__":
    eel.init("web")

    # Start main() in a separate thread
    main_thread = threading.Thread(target=run_main_in_thread)
    main_thread.start()

    eel.start("main.html")