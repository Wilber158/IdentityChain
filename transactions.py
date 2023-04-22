import keys

class Transactions:
    def __init__(self, sender, receiver, type, fields, transaction, signiture):
        self.sender_public_key = sender
        self.receiver_public_key = receiver
        self.signiture = signiture
        self.type = type
        self.transaction_data = transaction
        self.fields = fields #fields being modified or retrieved ex: name, ssn, address, DOB:....
    
