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
    def __init__(self):
        self.blockchain = BlockChain()
        self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.public_key().export_key().decode()
        self.mempool = []

    def create_transaction(self, receiver_public_key, data):
        hash = SHA256.new(data.encode())
        signature = PKCS1_PSS.new(self.private_key).sign(hash)
        return Transactions(self.public_key, receiver_public_key, signature.hex(), data)

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


def main():
    network = P2PNetwork()

    # Creating nodes
    node1 = FullNode()
    node2 = FullNode()
    node3 = FullNode()

    # Adding nodes to the network
    network.add_node(node1)
    network.add_node(node2)
    network.add_node(node3)

    # Node1 creates a transaction and broadcasts it to the network
    transaction1 = node1.create_transaction(node2.public_key, "Hello from Node1")
    network.broadcast_transaction(transaction1)

    # Node2 creates a transaction and broadcasts it to the network
    transaction2 = node2.create_transaction(node3.public_key, "Hello from Node2")
    network.broadcast_transaction(transaction2)

    # Node3 mines a block from its mempool and broadcasts the block to the network
    node3.mine_block()
    new_block = node3.blockchain.chain[-1]
    network.broadcast_block(new_block)

    # Print blockchain for all nodes
    for i, node in enumerate(network.nodes):
        print(f"Blockchain for Node{i + 1}:")
        for block in node.blockchain.chain:
            print(f"  Block {block.index}: {block.hash}")

if __name__ == "__main__":
    main()