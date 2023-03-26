import hashlib
import time


class block:
    def __init__(self, transactions, previous_hash):
        self.block_number = None
        self.merkle_root = createMerkle(transactions)
        self.timestamp = None
        self.previous_hash = previous_hash 
        self.hash = None
        self.transactions = transactions #In order to implement merkel trees this has to be turned into a tuple of transactions, where each is hashed and added as the merkel root of the block
    
    def verifyTransaction(self, transaction):
        hash_of_transaction = hashData(transaction)
        if hash_of_transaction in self.merkle_root:
            return True
        return False

    

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
    merkel = ""
    for i in transactions:
        i = hashData(i)
        merkel+= i
    return merkel



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
    string = ""
    while string is not "0":
        string = input("Enter a transaction you want to verify is in the blockchain: ")
        for i in chain.blocks:
            if i.verifyTransaction(string):
                print("found!!!!")
        print("Not in blockchain")

    
if __name__ == "__main__":
    main()
