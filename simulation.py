import time
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
import datetime
import os
from tkinter import filedialog
import hashlib
from transactions import generate_transaction_hash



class P2PNetwork:
    def __init__(self):
        self.nodes = []
        self.lightnodes = []
        self.userNodes = []

    def add_node(self, node):
        if isinstance(node, FullNode):
            self.nodes.append(node)
        elif isinstance(node, LightNode):
            self.lightnodes.append(node)
        elif isinstance(node, UserNode):
            self.userNodes.append(node)
    
    def add_user_node(self, node):
        print(f"adding {node}")
        self.userNodes.append(node)
        print("added")

    def broadcast_transaction(self, transaction):
        for node in self.nodes:
            node.receive_transaction(transaction)

    def broadcast_block(self, block, blockchain_size):
        for node in self.nodes:
            node.receive_block(block, blockchain_size)

def save_network(network, filename='network.pickle'):
    with open(filename, 'wb') as handle:
        pickle.dump(network, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("Network saved")

def load_network(filename='network.pickle'):
    with open(filename, 'rb') as handle:
        return pickle.load(handle)
    
network = P2PNetwork()


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
        for i in self.mempool:
            print(f"The following node is in the mempool ----> {i.sender_public_key}")

        if transaction.verify_signature():
            if transaction not in self.mempool: #Check for duplicate transactions
                self.mempool.append(transaction)
        else:
            print("Invalid transaction signature")

    def broadcast_block(self, block):
        for peer in network.nodes:
            if isinstance(peer, FullNode) and peer.pubkey_file != self.pubkey_file:
                peer.receive_block(block)

    def send_blockchain(self):
        return self.blockchain


    def receive_block(self, block, blockchain_size):
        if blockchain_size > self.blockchain.blockchain_size:            
            if self.blockchain.is_next_block(block):
                self.blockchain.addBlock(block)
                self.broadcast_block(block)
            else:
                self.sync_blockchain()

    def sync_blockchain(self):
        longest_blockchain = None
        max_length = 0

        for peer in network.nodes:
            if isinstance(peer, FullNode) and peer.pubkey_file != self.pubkey_file:
                blockchain = peer.send_blockchain()
                if blockchain.is_chain_valid() and len(blockchain.blocks) > max_length:
                    max_length = len(blockchain.blocks)
                    longest_blockchain = blockchain

        if longest_blockchain:
            self.blockchain = longest_blockchain


    def mine_block(self):
        if len(self.mempool) == 0:
            print("No transactions in mempool")
            return

        def is_user_node(transaction):
            for user_node in network.userNodes:
                if transaction.sender_public_key == user_node.pubkey_file:
                    return True
            return False

        # Prioritize user node transactions
        prioritized_mempool = sorted(self.mempool, key=is_user_node, reverse=True)

        # Select at most 4 transactions from the prioritized mempool
        transactions_to_mine = prioritized_mempool[:4]

        self.blockchain.addBlock(transactions_to_mine)

        # Remove the mined transactions from the mempool
        self.mempool = self.mempool[4:]

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
            node.receive_transaction(transaction)

class UserNode(LightNode):
    def __init__(self, priv_key, pub_key):
        self.privkey_file = priv_key
        self.pubkey_file = pub_key

def add_user_node(network, key_id, key_folder):
    user_node = UserNode(key_id, key_folder)
    network.add_node(user_node)
    return user_node


def generate_transaction_hash(transaction):
    # generate a hash value of the transaction data
    encrypted_hex = json.dumps(transaction)
    hash_value = hashlib.sha256(encrypted_hex.encode()).hexdigest()
    return hash_value


def save_blockchain(blockchain, filename='blockchain.pickle'):
    with open(filename, 'wb') as handle:
        pickle.dump(blockchain, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_blockchain(filename='blockchain.pickle'):
    with open(filename, 'rb') as handle:
        return pickle.load(handle)


def serialize_person_data(person_data):
    def convert(o):
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        raise TypeError(f'Object of type {type(o).__name__} is not JSON serializable')

    return json.dumps(person_data.__dict__, default=convert)

def simulateTransactions(network, new_nodes_queue):
    people = get_random_people()
    while True:
        # Check for new nodes in the queue
        while not new_nodes_queue.empty():
            new_node = new_nodes_queue.get()
            network.add_node(new_node)

        num_transactions = random.randint(1, 5)  # Random number of transactions per iteration
        for _ in range(num_transactions):
            time.sleep(15)  # Sleep for 1 second between transactions

            light_node = random.choice(network.lightnodes)
            receiver_node = random.choice([n for n in network.lightnodes if n != light_node])

            person_data = random.choice(people)
            person_data_json = serialize_person_data(person_data)

            print(f"Person data: {person_data_json}")  # Debug print
            
            transaction = light_node.create_transaction(receiver_node.pubkey_file, person_data_json)

            print(f"Transaction: {transaction}")  # Debug print

            light_node.send_transaction(transaction, network)

def simulateMining(network):
    while True: 
        time.sleep(10)
        full_node = random.choice([n for n in network.nodes if isinstance(n, FullNode)])
        full_node.mine_block()
        new_block = full_node.blockchain.blocks[-1]
        network.broadcast_block(new_block, full_node.blockchain.blockchain_size)  # Send the size

        # Save the blockchain
        save_blockchain(full_node.blockchain)
    


def main():
    global network
    print("Happening")
    num_full_nodes = 5
    num_light_nodes = 5
    key_folder = "keys"
    loaded = True
    for i in network.nodes:
        print(i)

    # Create the folder if it doesn't exist
    if not os.path.exists(key_folder):
        os.makedirs(key_folder)

     # Load the existing network if it exists
    try:
        network = load_network()
    except FileNotFoundError:
        network = P2PNetwork()
        loaded = False

    if not loaded:
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

    # Start the simulation for transactions in a separate thread
    transaction_simulation_thread = threading.Thread(target=simulateTransactions, args=(network, new_nodes_queue))
    transaction_simulation_thread.daemon = True  # Set the thread as a daemon to terminate with the main program
    transaction_simulation_thread.start()

    mining_simulation_thread = threading.Thread(target=simulateMining, args=(network,))
    mining_simulation_thread.daemon = True
    mining_simulation_thread.start()
        
    # Save the network after setting up the simulation

    save_network(network)


    while True:
        time.sleep(20)
        # Print blockchain for all full nodes
        for i, node in enumerate([n for n in network.nodes if isinstance(n, FullNode)]):
            print(f"________Blockchain for FullNode{i + 1}_______:")
            for block in node.blockchain.blocks:
                print(f"  Block {block.block_number}:\n\n\n")
                
                # Loop through the transactions in the block
                for transaction in block.transactions:
                    print(f"    Transaction: {transaction.transaction_data} \n\n\n")
                    print(f"      Sender Public Key: {transaction.sender_public_key} \n")
                    print(f"      Receiver Public Key: {transaction.receiver_public_key}\n")
                    print(f"Transaction contents: {transaction.transaction_data}\n")
                
                print(f"Timestamp: {block.timestamp} \n previous_hash: {block.previous_hash} \n hash: {block.hash}")

@eel.expose
def create_user_node(seed, file_name, file_dir):
    priv_dir = os.path.join(file_dir, f"{file_name}.pem")
    pub_dir = os.path.join(file_dir, f"{file_name}_pub.pem")
    print(f" Private key: {priv_dir}")
    print(pub_dir)
    print(f"{seed} type: {type(seed)}")
    keys.generate_ecc_private_key(seed, priv_dir)
    keys.generate_public_key(priv_dir, pub_dir)
    node = UserNode(priv_dir, pub_dir)
    network.add_user_node(node)
    print("Added to network")
    save_network(network)
    print(f"{network.userNodes}")

@eel.expose
def user_transaction(sender_privkey_file, sender_pubkey_file, receiver_pubkey_file, person_data_json, share_with_self):
    print(f"From GUI: {sender_privkey_file} {sender_pubkey_file}")
    print(f"Size: {len(network.userNodes)}")
    for user in network.userNodes:
        print(f"User Priv: {user.privkey_file} \n User_Pub:  {user.pubkey_file}")
    
    user_node = next((node for node in network.userNodes if node.privkey_file == sender_privkey_file and node.pubkey_file == sender_pubkey_file), None)

    if user_node:
        if share_with_self:
            receiver_pubkey_file = sender_pubkey_file

        transaction = user_node.create_transaction(receiver_pubkey_file, person_data_json)
        user_node.send_transaction(transaction, network)
        return "Transaction sent successfully."
    else:
        return "User node not found."

@eel.expose
def user_share_transaction(sender_privkey_file, sender_pubkey_file, receiver_pubkey_file, person_data_json):
    print(f"From GUI: {sender_privkey_file} {sender_pubkey_file} \n Receiver:{receiver_pubkey_file}")
    print(f"Size: {len(network.userNodes)}")
    for user in network.userNodes:
        print(f"User Priv: {user.privkey_file} \n User_Pub:  {user.pubkey_file}")

    user_node = next((node for node in network.userNodes if node.privkey_file.replace("\\", "/") == sender_privkey_file.replace("\\", "/") and node.pubkey_file.replace("\\", "/") == sender_pubkey_file.replace("\\", "/")), None)
    receiver_node = next((node for node in network.userNodes if node.pubkey_file == receiver_pubkey_file), None)
    
    if user_node and receiver_node:
        transaction = user_node.create_transaction(receiver_pubkey_file, person_data_json)
        user_node.send_transaction(transaction, network)
        print("Sent")
        return "Transaction sent successfully."
    else:
        return "User node not found."

    
@eel.expose
def get_user_transactions_eel(user_pubkey_file, user_privkey_file):
    return get_user_transactions(user_pubkey_file, user_privkey_file)

def get_user_transactions(user_pubkey_file, user_privkey_file):
    user_transactions = []

    # Load user's private key
    with open(user_privkey_file, 'rb') as f:
        user_priv_key_pem = f.read()

    # Load user's public key
    with open(user_pubkey_file, 'rb') as f:
        user_pub_key_pem = f.read()
 
    # Find a full node to access the blockchain
    full_node = next((node for node in network.nodes if isinstance(node, FullNode)), None)

    if full_node:
        print("Full node found")
        for block in full_node.blockchain.blocks:
            print("Block:", block)
            for transaction in block.transactions:
                print("Transaction:", transaction)
                if transaction.sender_public_key == user_pubkey_file or transaction.receiver_public_key== user_pubkey_file:
                    print("Matching transaction found")
                    
                    # Load sender's public key
                    with open(transaction.sender_public_key, 'rb') as f:
                        sender_pub_key_pem = f.read()

                    decrypted_data = keys.decrypt_transaction(sender_pub_key_pem, user_priv_key_pem, transaction.transaction_data)
                    transaction.transaction_data = json.loads(decrypted_data)  # Parse the decrypted data as JSON
                    user_transactions.append(transaction)

    return user_transactions

def run_main_in_thread():
    main()
    



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

@eel.expose
def select_file_directory():
    # Create a Tkinter root window
    root = tk.Tk()

    # Hide the root window to avoid it displaying during the file selection process
    root.withdraw()

    # Open a file selection dialog and get the selected file path
    selected_file = filedialog.askopenfilename()

    # Show the selected file path
    print("Selected file:", selected_file)

    # Return the selected file path
    return selected_file


if __name__ == "__main__":
    eel.init("web")
    # Start main() in a separate thread
    main_thread = threading.Thread(target=run_main_in_thread)
    main_thread.start()
    eel.start("main.html")


