from hash import hashData

class Block:
    def __init__(self, block_number, transactions, previous_hash, timestamp, nonce):
        self.block_number = block_number
        self.transactions = transactions
        self.timestamp = timestamp
        self.nonce = nonce
        self.previous_hash = previous_hash 
        self.hash = hashData(f"{block_number}{hashData(transactions)}{timestamp}{previous_hash}{nonce}")
    
    
    def mine(self, difficulty): #sets the hash value to its appropriate value
        while self.hash[:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = hashData(f"{self.block_number}{hashData(self.transactions)}{self.timestamp}{self.previous_hash}{self.nonce}")

    def calculate_hash(self):
        return hashData(f"{self.block_number}{hashData(self.transactions)}{self.timestamp}{self.previous_hash}{self.nonce}")
