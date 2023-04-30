from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Protocol.KDF import HKDF
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from mnemonic import Mnemonic
from transactions import Transactions
import json
from Crypto.Protocol.KDF import scrypt


#generate secret phrases
def generateMnemonicPhrase():
    mnemo = Mnemonic(language="english")
    words = mnemo.generate(strength=128)
    mnemonic_seed = mnemo.to_seed(words, passphrase="")
    return words


def generate_Mnemonic_private_key(mnemo_seed, filename, N=2**14, r=8, p=1):
    salt = get_random_bytes(16)
    key_material = scrypt(mnemo_seed, salt, 32, N, r, p)
    key_int = int.from_bytes(key_material, byteorder='big')
    key = RSA.construct((key_int,))

    with open(filename, 'wt') as f:
        f.write(key.export_key(format='PEM').decode())


def generate_private_key(filename):
    key = RSA.generate(2048)
    with open(filename, 'wt') as f:
        f.write(key.export_key(format='PEM').decode())


def generate_public_key(priv_dir, pub_dir):
    with open(priv_dir, 'rt') as f:
        key = RSA.import_key(f.read())
    
    with open(pub_dir, 'wt') as f:
        f.write(key.public_key().export_key(format='PEM').decode())

def generate_signiture(priv_dir, transaction):
    with open(priv_dir, 'rt') as f:
        priv_key = RSA.import_key(f.read())
    # creates signature object with the private key
    signature = PKCS1_PSS.new(priv_key)
    # create a hash object to hash the transaction
    hash = SHA256.new(transaction)
    
    # sign the signature with the transaction
    signed_hash = signature.sign(hash)
    return signed_hash

def encrypt_transaction(receiver_pubkey_pem, transaction):
    with open(receiver_pubkey_pem, 'rt') as f:
        receiver_pubkey = RSA.import_key(f.read())
    cipher = PKCS1_OAEP.new(receiver_pubkey)
    encrypted_transaction = cipher.encrypt(transaction.encode())
    return encrypted_transaction

def decrypt_transaction(privkey_dir, encrypted_transaction):
    with open(privkey_dir, 'rt') as f:
        privkey = RSA.import_key(f.read())

    cipher = PKCS1_OAEP.new(privkey)
    decrypted_transaction = cipher.decrypt(encrypted_transaction).decode()
    return decrypted_transaction

def verification_function(pub_dir, signature, transaction):
    with open(pub_dir, 'rt') as f:
        pub_key = RSA.import_key(f.read())

    # creates a signature object to be used for verification
    verifier = PKCS1_PSS.new(pub_key)
    # hash transaction
    hash = SHA256.new(transaction)
    
    # verify the signature
    try:
        verifier.verify(hash, signature)
        return True
    except ValueError:
        return False


def generate_transaction(priv_key_filename, sender_public, person, receiver_public=None):
    with open(priv_key_filename, 'rt') as f:
        priv_key = RSA.import_key(f.read())
    if receiver_public == None:
        encrypted_t = encrypt_transaction(sender_public, person)
        transaction = Transactions(sender_public, None, generate_signiture(priv_key_filename, encrypted_t), encrypted_t)
        return transaction
    else:
        encrypted_t = encrypt_transaction(receiver_public, person)
        transaction = Transactions(sender_public, receiver_public, generate_signiture(priv_key_filename, encrypted_t), encrypted_t)
        return transaction
    

def main():
    privkey = 'privatekey.pem'
    pubkey = 'publickey.pem'
    generate_private_key(privkey)
    generate_public_key(privkey, pubkey)

if __name__ == '__main__':
    main()
 



        

    



