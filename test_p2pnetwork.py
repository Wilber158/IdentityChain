import threading
import time
from blocks import Block
from blockchain import BlockChain
from protocol import P2PNetwork


def start_node(ip, port):
    blockchain = BlockChain()
    node = P2PNetwork(blockchain, ip, port)
    node.start()


def test_p2pnetwork():
    ip = "127.0.0.1"
    ports = [5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008]

    for port in ports:
        node_thread = threading.Thread(target=start_node, args=(ip, port))
        node_thread.start()
        time.sleep(1)  # To allow the node to start properly before starting the next one

    # Simulate interactions between nodes
    # You can add your own transactions, blocks, and sync requests to see how nodes interact
    


if __name__ == "__main__":
    test_p2pnetwork()
