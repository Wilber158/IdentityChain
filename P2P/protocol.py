import socket
import threading
import json
from queue import Queue
from kademlia.network import Server
from twisted.internet import reactor, defer

class P2PNetwork:
    def __init__(self, blockchain, ip, port):
        self.blockchain = blockchain
        self.ip = ip
        self.port = port
        self.peers = []
        self.incoming_messages = Queue()

    def start(self):
        server_thread = threading.Thread(target=self.listen_for_connections)
        server_thread.start()

        while True:
            print("Enter IP address and port of a peer to connect to (format: IP:PORT):")
            peer = input()
            ip, port = peer.split(":")
            self.connect_to_peer(ip, int(port))

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
            self.add_peer_to_dht(ip, port)  # Add connected peer to the DHT
        except Exception as e:
            print(f"Error connecting to {ip}:{port}: {e}")

    def handle_client(self, client_socket):
        peer_ip, peer_port = client_socket.getpeername()
        self.add_peer_to_dht(peer_ip, peer_port)  # Add connected peer to the DHT
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break

                message = data.decode()
                self.process_message(json.loads(message))
            except Exception as e:
                print(f"Error receiving data: {e}")
                break

        client_socket.close()
        self.peers.remove(client_socket)
        print("Peer disconnected")

    def broadcast(self, message):
        for peer in self.peers:
            try:
                peer.sendall(json.dumps(message).encode())
            except Exception as e:
                print(f"Error sending message: {e}")

    def process_message(self, message):
        if message["type"] == "new_block":
            block = message["data"]
            if self.blockchain.validate_and_add_block(block):
                print("New block added to the blockchain")
                self.broadcast(message) 

    def send_new_block(self, block):
        message = {
            "type": "new_block",
            "data": block
        }
        self.broadcast(message)

    def start_kademlia(self, bootstrap_node=None):
        self.kademlia = Server()
        self.kademlia.listen(self.port)
        if bootstrap_node:
            bootstrap_node = tuple(bootstrap_node.split(":"))
            d = self.kademlia.bootstrap([(bootstrap_node[0], int(bootstrap_node[1]))])
            d.addCallback(self.bootstrap_done)
        else:
            self.bootstrap_done(None)

    def bootstrap_done(self, result):
        print("Kademlia bootstrap done")
        self.start()

    def add_peer_to_dht(self, ip, port):
        d = self.kademlia.set(ip, f"{ip}:{port}")
        d.addCallback(self.added_peer_to_dht)

    def outbound_node_disconnected(self, connected_node):
        print("outbound_node_disconnected: " + connected_node.id)

    def node_message(self, connected_node, data):
        print("node_message from " + connected_node.id + ": " + str(data))
        
    def node_disconnect_with_outbound_node(self, connected_node):
        print("node wants to disconnect with oher outbound node: " + connected_node.id)
        
    def node_request_to_stop(self):
        print("node is requested to stop!")