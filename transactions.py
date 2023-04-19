import keys

class Transactions:
    def __init__(self, sender, receiver, transaction):
        self.sender_public_key = sender
        self.receiver_public_key = receiver
        self.transaction_data = transaction

    def encrypt(transaction):
        return keys.generate_signiture()

    
