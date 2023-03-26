from hash import hashData

class Block:
    def __init__(self, block_number, transactions, previous_hash, timestamp, nonce):
        self.block_number = block_number
        self.transactions = transactions
        self.merkle_root = createMerkle(transactions)
        self.timestamp = timestamp
        self.nonce = nonce
        self.previous_hash = previous_hash 
        self.hash = hashData(f"{block_number}{hashData(transactions)}{self.merkle_root}{timestamp}{previous_hash}{nonce}")
    
    def verifyTransaction(self, transaction):
        hash_of_transaction = hashData(transaction)
        if hash_of_transaction in self.merkle_root:
            return True
        return False

def createMerkle(transactions):
    merkel = ""
    for i in transactions:
        i = hashData(i)
        merkel+= i
    return transactions
