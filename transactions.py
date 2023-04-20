import keys

class Transactions:
<<<<<<< Updated upstream
    def __init__(self, sender, receiver, transaction):
        self.sender_public_key = sender
        self.receiver_public_key = receiver
        self.transaction_data = transaction

    def encrypt(transaction):
        return keys.generate_signiture()
=======
    def __init__(self, sender, receiver, type, transaction):
        self.sender = sender
        self.receiver = receiver
        self.type = type
        self.transaction = transaction
>>>>>>> Stashed changes

    
