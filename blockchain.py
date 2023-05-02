import hashlib
import time
from hash import hashData
from blocks import Block

class Transactions:
    def __init__(self, sender, receiver, transaction, signature):
        self.sender_public_key = sender
        self.receiver_public_key = receiver#none if first transaction
        self.signature = signature
        self.transaction_data = transaction #only this field is encrypted

class BlockChain:
    def __init__(self):
        #creates genesis block, while initializing default variables
        self.genesis = Block(0, [Transactions(None, None, None, None)], None, time.time(), 0)
        self.blocks = [self.genesis]
        self.blockchain_size = 1
        self.difficulty = 2
    
    def addBlock(self, transactions, nonce=0):
        #Check for double spending        
        for block in self.blocks:
            for t in transactions:
                if t in block.transactions:
                    print("Transaction already in chain!")
                    return

        previous_hash = self.blocks[-1].hash
        #creating the block
        new_block = Block(self.blockchain_size, transactions, previous_hash, time.time(), nonce)
        new_block.mine(self.difficulty)
        #adding it to the blockchain
        self.blocks.append(new_block)
        #incrementing the number of blocks in the chain
        self.blockchain_size += 1

    def is_next_block(self, block):
        last_block = self.blocks[-1]
        if block.block_number != last_block.block_number + 1:
            return False
        if block.previous_hash != last_block.hash:
            return False
        if block.hash != block.calculate_hash():
            return False
        return True


    def is_chain_valid(self):
        for i in range(1, len(self.blocks)):
            current_block = self.blocks[i]
            previous_block = self.blocks[i - 1]

            # Check if the current block's hash is correct
            if current_block.hash != current_block.calculate_hash():
                return False

            # Check if the current block's previous_hash field matches the previous block's hash
            if current_block.previous_hash != previous_block.hash:
                return False

        return True


