import hashlib
import secrets
import random
import time
import string


class block:
    blockNum = 0
    prevHash = None
    hash = None
    data = ""
    next = None
    

class blockChain:
    def __init__(self, head):
        self.head = head
        self.tail = head


def createBlock(data):
    blockNum = random.uniform(0, 2131231412)
    newBlock = block()
    newBlock.data = data
    newBlock.blockNum = blockNum
    newBlock.hash = hashData(data)
    newBlock.prevHash = None
    return newBlock

def addBlock(chain, block):
    prevHash = chain.tail.hash
    block.prevHash = prevHash
    chain.tail.next = block
    chain.tail = block
    return chain

def createBlockChain(block):
    chain = blockChain(block)
    return chain
    
def hashData(data):
    hash = hashlib.sha256(data.encode()).hexdigest()
    return hash

def hash_Input(zeros):
    attempts = 0
    str = ''
    found = False
    while not found:
        randomMessage = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(15))
        output = hashlib.sha256(randomMessage.encode())
        output = output.hexdigest()
        if output.startswith(zeros):
            return randomMessage, output

def printBlockchain(chain):
    current = chain.head
    while current is not None:
        print(f"Block Number: {current.blockNum} \nData: {current.data}\nPrevious Hash: {current.prevHash}\
            \nHash: {current.hash} \n")
        current = current.next


def main():
    data = 1
    iterations = 0
    chain = None
    print(f"Enter [0] to quit from the program")
    while not (data == "0"):
        data = input("Please enter some data to be added to a blockchain: ")
        if(data == "0"): break
        if(iterations == 0):
            block = createBlock(data)
            chain = blockChain(block)
            iterations += 1
        else:
            block = createBlock(data)
            chain = addBlock(chain, block)
    
    printBlockchain(chain)

    

main()
