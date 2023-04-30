import keys

class Transactions:
    def __init__(self, sender, receiver, transaction, signature):
        self.sender_public_key = sender
        self.receiver_public_key = receiver#none if first transaction
        self.signature = signature
        self.transaction_data = transaction #only this field is encrypted
    
    def verify_signature(self):
        return keys.verification_function(self.sender_public_key, self.signature, self.transaction_data)
            
