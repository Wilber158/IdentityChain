import hashlib
import time


class block:
    def __init__(self, transactions, previous_hash):
        block_number = None
        merkle_root = None
        timestamp = None
        self.previous_hash = previous_hash 
        hash = None
        self.transactions = transactions #In order to implement merkel trees this has to be turned into a tuple of transactions, where each is hashed and added as the merkel root of the block
    

class blockChain:
    def __init__(self):
        #creates genesis block, while initializing default variables
        self.genesis = block(["abc"], None)
        self.genesis.hash = hashData(self.genesis.transactions)
        self.genesis.timestamp = time.time()
        self.genesis.block_number = 0
        self.blocks = [self.genesis]
        self.blockchain_size = 1
    
    def addBlock(self, transactions):
        previous_hash = self.blocks[-1].hash
        #creating the block
        new_block = block(transactions, previous_hash)
        new_block.block_number = self.blockchain_size
        new_block.transactions = transactions
        new_block.hash = hashData(transactions)
        new_block.timestamp = time.time()

        #adding it to the blockchain
        self.blocks.append(new_block)

        #incrementing the number of blocks in the chain
        self.blockchain_size += 1

    
def hashData(data):
    string = ""
    if type(data) == list:
        for i in data:
            string += i
        hash = hashlib.sha256(string.encode()).hexdigest()
        return hash

    hash = hashlib.sha256(data.encode()).hexdigest()
    return hash

def createMerkle(transactions):
    pass



def printBlockchain(chain):
    for current in chain.blocks:
        print(f"Block Number: {current.block_number} \nData: {current.transactions}\nPrevious Hash: {current.previous_hash}\
            \nHash: {current.hash} \nTimestamp: {current.timestamp}")

def main():
    data = 1
    iterations = 0
    chain = blockChain()
    print(f"Enter [0] to quit from the program")
    while not (data == "0"):
        data = [input("Please enter some data to be added to a blockchain: ")]
        if(data[0] == "0"): break
        chain.addBlock(data)

    printBlockchain(chain)

    
if __name__ == "__main__":
    main()
