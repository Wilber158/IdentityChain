from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import HKDF
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from mnemonic import Mnemonic
from transactions import Transactions
import json
from Crypto.Protocol.KDF import scrypt
import eel
import binascii
import os
import base64
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

#generate secret phrases
@eel.expose
def generateMnemonicPhrase():
    mnemo = Mnemonic(language="english")
    words = mnemo.generate(strength=128)
    mnemonic_seed = mnemo.to_seed(words, passphrase="")
    result = {"words": words, "seed": mnemonic_seed.hex()}  # Convert the seed to a hexadecimal string
    return json.dumps(result)

def generateMnemonicPhrase2():
    mnemo = Mnemonic(language="english")
    words = mnemo.generate(strength=128)
    mnemonic_seed = mnemo.to_seed(words, passphrase="")
    return mnemonic_seed

def generate_private_key(filename):
    curve = "secp256r1"
    key = ECC.generate(curve=curve)
    with open(filename, 'wb') as f:
        f.write(key.export_key(format='PEM').encode())

def generate_ecc_private_key(seed, priv_dir):
    curve = "secp256r1"

    def custom_randfunc(n):
        drbg = HKDF(
            algorithm=hashes.SHA256(),
            length=n,
            salt=None,
            info=None,
            backend=default_backend()
        )
        return drbg.derive(seed.encode('utf-8'))

    key = ECC.generate(curve=curve, randfunc=custom_randfunc)
    print("generated")
    with open(priv_dir, 'wb') as f:
        f.write(key.export_key(format='PEM').encode())
    print("Private key generated and stored at:", priv_dir)

def generate_public_key(priv_dir, pub_dir):
    with open(priv_dir, 'rt') as f:
        key = ECC.import_key(f.read())
    with open(pub_dir, 'wt') as f:
        f.write(key.public_key().export_key(format='PEM'))

def generate_user_key(priv_dir, pub_dir, file_dir):
    with open(f"{file_dir}/{priv_dir}", 'rt') as f:
        key = ECC.import_key(f.read())

    with open(f"{file_dir}/{pub_dir}", 'wt') as f:
        f.write(key.public_key().export_key(format='PEM'))

def generate_signiture(priv_dir, encrypted_data):
    with open(priv_dir, 'rt') as f:
        priv_key = ECC.import_key(f.read())
    # creates signature object with the private key
    signature = DSS.new(priv_key, 'fips-186-3')
    # create a hash object to hash the transaction
    encrypted_hex = json.dumps(encrypted_data)
    hash = SHA256.new()
    hash.update(encrypted_hex.encode())
    
    # sign the signature with the transaction
    signed_hash = signature.sign(hash)
    return signed_hash

def encrypt_transaction(sender_priv_key_pem, receiver_pub_key_pem, data):
    # Load private key
    private_key = serialization.load_pem_private_key(sender_priv_key_pem, password=None, backend=default_backend())

    # Load public key
    public_key = serialization.load_pem_public_key(receiver_pub_key_pem, backend=default_backend())

    # Derive shared secret
    shared_secret = private_key.exchange(ec.ECDH(), public_key)
    
    # Derive encryption key using HKDF
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=None,
        backend=default_backend()
    ).derive(shared_secret)

    # Encrypt data
    aesgcm = AESGCM(derived_key)
    nonce = os.urandom(12)
    encrypted_data = aesgcm.encrypt(nonce, str(data).encode('utf-8'), None)
    encrypted_data_b64 = base64.b64encode(encrypted_data).decode('utf-8')


    return {'ciphertext': encrypted_data_b64, 'nonce': str(nonce)}



def decrypt_transaction(sender_pub_key_pem, receiver_priv_key_pem, encrypted_data):
    # Load public key
    public_key = serialization.load_pem_public_key(sender_pub_key_pem, backend=default_backend())

    # Load private key
    private_key = serialization.load_pem_private_key(receiver_priv_key_pem, password=None, backend=default_backend())

    # Derive shared secret
    shared_secret = private_key.exchange(ec.ECDH(), public_key)

    # Derive decryption key using HKDF
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=None,
        backend=default_backend()
    ).derive(shared_secret)

    # Decrypt data
    aesgcm = AESGCM(derived_key)
    decrypted_data = aesgcm.decrypt(encrypted_data['nonce'], encrypted_data['ciphertext'], None)

    return decrypted_data.decode('utf-8')


def verification_function(pub_dir, signature, transaction):
    with open(pub_dir, 'rt') as f:
        pub_key = ECC.import_key(f.read())

    # creates a signature object to be used for verification
    verifier = DSS.new(pub_key, 'fips-186-3')
    # hash transaction
    encrypted_hex = json.dumps(transaction)
    hash = SHA256.new(encrypted_hex.encode())
    
    # verify the signature
    try:
        verifier.verify(hash, signature)
        return True
    except ValueError:
        return False

def generate_transaction(sender_priv_key_filename, sender_pub_key_filename, data, receiver_pub_key_filename):
    with open(sender_priv_key_filename, 'rb') as f:
        sender_priv_key_pem = f.read()

    with open(sender_pub_key_filename, 'rb') as f:
        sender_pub_key_pem = f.read()

    with open(receiver_pub_key_filename, 'rb') as f:
        receiver_pub_key_pem = f.read()

    encrypted_t = encrypt_transaction(sender_priv_key_pem, receiver_pub_key_pem, data)
    print(f"Encrypted Data: {encrypted_t}")
    transaction = Transactions(sender_pub_key_filename, receiver_pub_key_filename, encrypted_t, generate_signiture(sender_priv_key_filename, encrypted_t))
    return transaction



    


