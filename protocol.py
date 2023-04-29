import socket
import threading
import json
import keys
import pickle
import time
import random
import person
from person import get_random_people

class P2PNetwork:
    def __init__(self, blockchain, ip, port, public, private):
        self.blockchain = blockchain
        self.ip = ip
        self.port = port
        self.pub_key = public
        self.priv_key = private
        self.peers = []
        self.mempool = []

    def start(self):
        server_thread = threading.Thread(target=self.listen_for_connections)
        server_thread.start()

        sync_thread = threading.Thread(target=self.start_sync, args=(60,))  # Sync every 60 seconds
        sync_thread.start()
        
    def request_sync(self):
        message = {
            "type": "sync_request"
        }
        self.broadcast(message)

    def start_sync(self, sync_interval):
        while True:
            time.sleep(sync_interval)
            self.request_sync()

    def send_sync_response(self, client_socket):
        message = {
            "type": "sync_response",
            "mempool": pickle.dumps(self.mempool),
            "blockchain": pickle.dumps(self.blockchain)
        }
        try:
            client_socket.sendall(json.dumps(message).encode())
        except Exception as e:
            print(f"Error sending sync response: {e}")

    def listen_for_connections(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(10)
        print(f"Listening for connections on {self.ip}:{self.port}")
        
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            self.peers.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def connect_to_peer(self, ip, port):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((ip, port))
            print(f"Connected to {ip}:{port}")
            self.peers.append(peer_socket)
            threading.Thread(target=self.handle_client, args=(peer_socket,)).start()
        except Exception as e:
            print(f"Error connecting to {ip}:{port}: {e}")

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break

                message = data.decode()
                received_message = json.loads(message)

                if received_message["type"] == "new_block":
                    block_data = received_message["data"]
                    block = pickle.loads(block_data)
                    self.process_newBlock(block)
                elif received_message["type"] == "new_transaction":
                    transaction_data = received_message["data"]
                    transaction = pickle.loads(transaction_data)
                    if transaction not in self.mempool:  # Check if the transaction is not already in the mempool
                        self.process_transaction(transaction)
                elif received_message["type"] == "sync_request":
                    self.send_sync_response(client_socket)
                
                elif received_message["type"] == "sync_response":
                    received_mempool = pickle.loads(received_message["mempool"])
                    received_blockchain = pickle.loads(received_message["blockchain"])
                    self.update_mempool(received_mempool)
                    self.update_blockchain(received_blockchain)
                else:
                    pass
                    # Process other message types
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

    def broadcast(self, message):
        for peer_socket in self.peers:
            try:
                peer_socket.sendall(json.dumps(message).encode())
            except Exception as e:
                print(f"Error sending message: {e}")

    def update_mempool(self, received_mempool):
        for transaction in received_mempool:
            if transaction not in self.mempool:
                self.process_transaction(transaction)

    def update_blockchain(self, received_blockchain):
        if len(received_blockchain.chain) > len(self.blockchain.chain):
            if received_blockchain.is_chain_valid():
                self.blockchain = received_blockchain
                print("Blockchain updated.")

    def process_transaction(self, transaction):
        public_key = transaction.sender_public_key
        signature = transaction.signature
        data = transaction.transaction_data
        isValid = keys.verification_function(public_key, signature, data)
        if isValid:
            self.mempool.append(transaction)
            self.send_transaction(transaction)
    
    def send_transaction(self, transaction):
        message = {
            "type": "new_transaction",
            "data": pickle.dumps(transaction)
        }
        self.broadcast(message)
    
    def process_newBlock(self, block):
        if self.blockchain.is_chain_valid():
            if block.previous_hash == self.blockchain.chain[-1].hash:
                if block.hash == block.calculate_hash():
                    self.blockchain.add_block(block)
                    print("Block added to the blockchain.")

                    # Remove the transactions in the block from the mempool
                    for transaction in block.transactions:
                        if transaction in self.mempool:
                            self.mempool.remove(transaction)
                else:
                    print("Invalid block hash.")
            else:
                print("Invalid previous block hash.")
        else:
            print("Invalid blockchain.")
    
    def send_new_block(self, block):
        message = {
            "type": "new_block",
            "data": block
        }
        self.broadcast(message)

class LightNode:
    def __init__(self, ip, port, public_key, private_key, full_nodes):
        self.ip = ip
        self.port = port
        self.pub_key = public_key
        self.priv_key = private_key
        self.full_nodes = full_nodes

    def connect_to_full_node(self):
        for node_ip, node_port in self.full_nodes:
            try:
                full_node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                full_node_socket.connect((node_ip, node_port))
                print(f"Light node connected to {node_ip}:{node_port}")
                return full_node_socket
            except Exception as e:
                print(f"Error connecting to {node_ip}:{node_port}: {e}")

    def create_transaction(self,transaction_data):
        transaction = keys.generate_transaction(self.priv_key, self.pub_key, 'store', transaction_data)
        return transaction

    def send_transaction(self, transaction, full_node_socket):
        message = {
            "type": "new_transaction",
            "data": pickle.dumps(transaction)
        }
        try:
            full_node_socket.sendall(json.dumps(message).encode())
        except Exception as e:
            print(f"Error sending transaction: {e}")

    def simulate_transactions(self, other_nodes_public_keys):
        full_node_socket = self.connect_to_full_node()
        while True:
            randomTime =  random.randint(10-100)
            time.sleep(randomTime)  # Adjust the time between transactions if needed
            receiver_public_key = random.choice(other_nodes_public_keys)
            person = get_random_people()
            ranIndex = random.randint(0-18)
            transaction = self.create_transaction(receiver_public_key, person[ranIndex])
            self.send_transaction(transaction, full_node_socket)