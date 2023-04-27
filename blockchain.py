import hashlib
import time
from hash import hashData
from blocks import *
from transactions import Transactions


class BlockChain:
    def __init__(self):
        #creates genesis block, while initializing default variables
        self.genesis = Block(0, ["genesis"], None, time.time(), 0)
        self.blocks = [self.genesis]
        self.blockchain_size = 1
    
    def addBlock(self, transactions, nonce):
        previous_hash = self.blocks[-1].hash
        #creating the block
        new_block = Block(self.blockchain_size, transactions, previous_hash, time.time(), nonce)

        #adding it to the blockchain
        self.blocks.append(new_block)

        #incrementing the number of blocks in the chain
        self.blockchain_size += 1
    def verify_add_block(self, block):
        prevHash = self.blocks[-1].hash
        
    


def printBlockchain(chain):
    for current in chain.blocks:
        print(f"Block Number: {current.block_number} \nData: {current.transactions}\nPrevious Hash: {current.previous_hash}\
            \nHash: {current.hash} \nTimestamp: {current.timestamp}")

def main():
    data = 1
    iterations = 0
    chain = BlockChain()
    print(f"Enter [0] to quit from the program")
    while not (data == "0"):
        data = [input("Please enter some data to be added to a blockchain: ")]
        if(data[0] == "0"): break
        chain.addBlock(data, 0)

    printBlockchain(chain)
    string = ""
    while string != "0":
        string = input("Enter a transaction you want to verify is in the blockchain: ")
        for i in chain.blocks:
            if i.verifyTransaction(string):
                print("found!!!!")
        print("Not in blockchain")

    
if __name__ == "__main__":
    main()
