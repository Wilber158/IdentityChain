import hashlib
import time


class block:
    blockNum = 0
    timestamp = None
    prevHash = None
    hash = None
    data = "" #In order to implement merkel trees this has to be turned into a tuple of transactions, where each is hashed and added as the merkel root of the block
    next = None


def createBlock(data):
    newBlock = block()
    newBlock.data = data
    newBlock.hash = hashData(data)
    newBlock.prevHash = None
    newBlock.timestamp = time.time()
    return newBlock

    

class blockChain:
    def __init__(self):
        #creates genesis block, while initializing default variables
        self.genesis = createBlock("abc")
        self.head = self.genesis
        self.tail = self.genesis
        self.genesis.blockNum = 0
        self.blockchain_size = 1
    
    def addBlock(self, data):
        #creating the block
        newBlock = createBlock(data)
        newBlock.blockNum = self.blockchain_size

        #adding it to the blockchain
        prevHash = self.tail.hash
        newBlock.prevHash = prevHash
        self.tail.next = newBlock
        self.tail = newBlock
        #incrementing the number of blocks in the chain
        self.blockchain_size += 1

    
def hashData(data):
    hash = hashlib.sha256(data.encode()).hexdigest()
    return hash


def printBlockchain(chain):
    current = chain.head
    while current is not None:
        print(f"Block Number: {current.blockNum} \nData: {current.data}\nPrevious Hash: {current.prevHash}\
            \nHash: {current.hash} \nTimestamp: {current.timestamp}")
        current = current.next


def main():
    data = 1
    iterations = 0
    chain = blockChain()
    print(f"Enter [0] to quit from the program")
    while not (data == "0"):
        data = input("Please enter some data to be added to a blockchain: ")
        if(data == "0"): break
        chain.addBlock(data)

    printBlockchain(chain)

    

main()
