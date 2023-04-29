import threading
import time
from blocks import Block
from blockchain import BlockChain
from protocol import P2PNetwork
from protocol import LightNode
import keys
from Crypto.PublicKey import ECC



def start_node(ip, port, public_key, private_key, blockchain):
    node = P2PNetwork(blockchain, ip, port, public_key, private_key)
    node.start()

def generate_key_pairs(num_nodes):
    key_pairs = []

    for _ in range(num_nodes):
        private_key_filename = 'private_key.pem'
        public_key_filename = 'public_key.pem'

        keys.generate_private_key(private_key_filename)
        keys.generate_public_key(private_key_filename, public_key_filename)

        with open(private_key_filename, 'rt') as f:
            private_key = f.read()

        with open(public_key_filename, 'rt') as f:
            public_key = f.read()

        key_pairs.append((public_key, private_key))

    return key_pairs


def generate_key_pairs(num_nodes):
    key_pairs = []

    for _ in range(num_nodes):
        private_key_filename = 'private_key.pem'
        public_key_filename = 'public_key.pem'

        keys.generate_private_key(private_key_filename)
        keys.generate_public_key(private_key_filename, public_key_filename)

        with open(private_key_filename, 'rt') as f:
            private_key = f.read()

        with open(public_key_filename, 'rt') as f:
            public_key = f.read()

        key_pairs.append((public_key, private_key))

    return key_pairs


def create_transaction_and_mine_block(node, sender_private_key, receiver_public_key, transaction_data):
    # Create a transaction
    transaction = keys.generate_transaction(sender_private_key, receiver_public_key, transaction_data)

    # Add the transaction to the mempool
    node.process_transaction(transaction)

    # Mine a block if there are enough transactions in the mempool
    if len(node.mempool) >= 5:  # Set the minimum number of transactions required to mine a block
        new_block = node.blockchain.create_block(node.mempool)
        node.send_new_block(new_block)
        node.mempool.clear()


def test_p2pnetwork():
    ip = "127.0.0.1"
    ports = [5001, 5002, 5003, 5004, 5005, 5006, 5007, 5008]
    num_light_nodes = 4

    # Generate key pairs for light nodes
    light_node_key_pairs = generate_key_pairs(num_light_nodes)
    light_nodes_public_keys = [public_key for public_key, _ in light_node_key_pairs]

    for port in ports:
        # Generate a key pair for the full node
        key = ECC.generate(curve='P-256')
        public_key = key.public_key().export_key(format='PEM')
        private_key = key.export_key(format='PEM')

        # Create a new blockchain instance for the full node
        blockchain = BlockChain()

        # Initialize the full node with the blockchain instance, public, and private keys
        full_node_thread = threading.Thread(target=start_node, args=(blockchain, ip, port, public_key, private_key))
        full_node_thread.start()
        time.sleep(1)  # To allow the node to start properly before starting the next one

    for idx, (public_key, private_key) in enumerate(light_node_key_pairs):
        light_node = LightNode(ip, 6000 + idx, public_key, private_key, [(ip, port) for port in ports])
        light_node_thread = threading.Thread(target=light_node.simulate_transactions, args=(light_nodes_public_keys,))
        light_node_thread.start()
        time.sleep(1)  # To allow the light node to start properly before starting the next one

if __name__ == "__main__":
    test_p2pnetwork()



    


if __name__ == "__main__":
    test_p2pnetwork()
