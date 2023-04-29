import socket
import threading
import json
import keys
import pickle
import time
import random
import person
from person import get_random_people
import base64
from signal import signal, SIGPIPE, SIG_DFL  
signal(SIGPIPE,SIG_DFL)
  


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

        mine_thread = threading.Thread(target=self.mine_new_block, args=(random.randint(0, 100),))
        
    def request_sync(self):
        message = {
            "type": "sync_request"
        }
        self.broadcast(message)

    def start_sync(self, sync_interval):
        while True:
            time.sleep(sync_interval)
            self.request_sync()
    
    def mine_new_block(self):
        while True:


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
        try: 
            while True:
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
                        transaction = pickle.loads(base64.b64decode(transaction_data))
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
        except (BrokenPipeError, ConnectionResetError):
            print(f"Connection closed by client {client_socket.getpeername()}")
            client_socket.close()
            self.peers.remove(client_socket)
            

    def broadcast(self, message):
        for peer_socket in self.peers:
            peer_socket.sendall(json.dumps(message).encode())

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
        data = transaction.transaction_data #persons object should be here
        isValid = keys.verification_function(public_key, signature, data)
        if isValid:
            self.mempool.append(transaction)
            self.send_transaction(transaction)

            
    
    def send_transaction(self, transaction):
        message = {
            "type": "new_transaction",
            "data": base64.b64encode(pickle.dumps(transaction)).decode()
        }
        peers_to_remove = []
        for idx, peer_socket in enumerate(self.peers):
            try:
                peer_socket.sendall(json.dumps(message).encode())
            except BrokenPipeError as e:
                print(f"Broken pipe error in send_transaction at index {idx}: {e}")
                peers_to_remove.append(idx)
            except Exception as e:
                print(f"Error sending transaction at index {idx}: {e}")

        for idx in reversed(peers_to_remove):
            peer_socket = self.peers.pop(idx)
            peer_socket.close()
            print(f"Removed broken connection at index {idx}")
    
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
    def __init__(self, ip, port, public_key_filename, private_key_filename, peers):
        self.ip = ip
        self.port = port
        self.public_key = public_key_filename
        self.private_key = private_key_filename
        self.peers = peers

    def connect_to_full_node(self):
        for node_ip, node_port in self.peers:
            try:
                full_node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                full_node_socket.connect((node_ip, node_port))
                print(f"Light node connected to {node_ip}:{node_port}")
                return full_node_socket
            except Exception as e:
                print(f"Error connecting to {node_ip}:{node_port}: {e}")

    def create_transaction(self,transaction_data, person):
        transaction = keys.generate_transaction(self.private_key, self.public_key, 'store', person)
        return transaction

    def send_transaction(self, transaction):
        full_node_socket = self.connect_to_full_node()
        message = {
            "type": "new_transaction",
            "data": base64.b64encode(pickle.dumps(transaction)).decode()
        }
        try:
            full_node_socket.sendall(json.dumps(message).encode())
        except Exception as e:
            print(f"Error sending transaction in lightnodes: {e}")


    def simulate_transactions(self, other_nodes_public_keys):
        while True:
            randomTime = random.randint(10, 30)
            time.sleep(randomTime)  # Adjust the time between transactions if needed
            receiver_public_key = random.choice(other_nodes_public_keys)
            person = get_random_people()
            ranIndex = random.randint(0, 17)
            transaction = self.create_transaction(receiver_public_key, person[ranIndex])
            self.send_transaction(transaction)
