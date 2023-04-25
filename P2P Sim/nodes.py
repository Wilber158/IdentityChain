

'''
Full Nodes:
Maintain a complete copy of the blockchain, including all blocks and transactions.
Validate all transactions and blocks according to the consensus rules.
Broadcast new transactions and blocks to their peers.
Serve as a reference point for other nodes, providing them with information about the blockchain's state.
'''

class FullNode:
    def __init__(self):
        self.node_id
        self.peers
        self.blockchain_copy
        self.mempool
        self.public_key
        pass

    def connect_to_peer():
        pass
    def broadcast_transaction():
        pass
    def broadcast_block():
        pass
    def recieve_transaction():
        pass
    def receive_block():
        pass
    def mine_block():
        pass

    
'''Light Nodes
Store only the block headers and a minimal subset of transactions relevant to the node.
Rely on Full nodes for blockchain information and transaction validation.
Can create and broadcast new transactions, but don't validate or relay all transactions.
'''
class LightNode:
    def __init__(self):
        self.node_id
        self.blockchain #merkle root of all blocks
        self.peers
        self.block_headers
        self.transactions #transactions relevant to that node would be called when connected to a full node
        self.public_key #the public key for this respective node
        pass
    
    def connect_to_peer():
        pass
    def request_transaction():
