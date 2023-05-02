from Crypto.PublicKey import ECC
from Crypto.Signature import PKCS1_PSS
from Crypto.Signature import DSS
from Crypto.Protocol.KDF import HKDF
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
import json
import hashlib
class Transactions:
    def __init__(self, sender, receiver, transaction, signature, isUser=None):
        self.sender_public_key = sender
        self.receiver_public_key = receiver#none if first transaction
        self.signature = signature
        self.transaction_data = transaction #only this field is encrypted
        self.isUser = isUser
    
    def verify_signature(self):
        return verification_function(self.sender_public_key, self.signature, self.transaction_data)
    
    def __str__(self):
        return f"Transactions(sender_public_key={self.sender_public_key}, receiver_public_key={self.receiver_public_key}, signature={self.signature}, data={self.transaction_data})"

    

def verification_function(pub_dir, signature, transaction):
    with open(pub_dir, 'rt') as f:
        pub_key = ECC.import_key(f.read())
    # creates a signature object to be used for verification
    verifier = DSS.new(pub_key, 'fips-186-3')
    # hash transaction
    encrypted_hex = json.dumps(transaction)
    hash = SHA256.new()
    hash.update(encrypted_hex.encode())
    
    # verify the signature
    try:
        verifier.verify(hash, signature)
        return True
    except ValueError:
        return False

def generate_transaction_hash(transaction):
    # generate a hash value of the transaction data
    encrypted_hex = json.dumps(transaction.transaction_data)
    hash_value = hashlib.sha256(encrypted_hex.encode()).hexdigest()
    return hash_value
