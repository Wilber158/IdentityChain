import keys

class Transactions:
    def __init__(self, sender, receiver, type, fields, transaction, signiture):
        self.sender_public_key = sender
        self.receiver_public_key = receiver#none if first transaction
        self.signiture = signiture
        self.type = type
        self.transaction_data = transaction #only this field is encrypted
        self.fields = fields #when first transaction None#fields being modified or retrieved ex: name, ssn, address, DOB:....    
    
    def verify_signature(self):
        return keys.verification_function(self.sender_public_key, self.signature, self.transaction_data)
            
