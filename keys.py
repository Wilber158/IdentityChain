from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256


def generate_private_key(filename):
    key = ECC.generate(curve='P-256')
    with open(filename, 'wt') as f:
        f.write(key.export_key(format='PEM'))
    


def generate_public_key(priv_dir, pub_dir):
    with open(priv_dir, 'rt') as f:
        key =  ECC.import_key(f.read())
    
    with open(pub_dir, 'wt') as f:
        f.write(key.public_key().export_key(format='PEM'))
    

def generate_signiture(priv_dir, transaction):
    with open(priv_dir, 'rt') as f:
        priv_key =  ECC.import_key(f.read())
    #creates signiture object with the private key
    signature = DSS.new(priv_key)
    #create a hash object to hash the transaction
    hash = SHA256.new(transaction)
    
    #sign the signiture with the transaction
    signature.sign(hash)
    
    return signature


def verification_function(pub_dir, signature, transaction):
    with open(pub_dir, 'rt') as f:
        pub_key =  ECC.import_key(f.read())

    #creates a signiture object to be used for verification
    verifier = DSS.new(pub_key)
    #hash transaction
    hash = SHA256.new(transaction)
    
    #verify the signiture
    try:
        verifier.verify(hash, signature)
        print("Signiture is valid!") #return true
    except ValueError:
        print("Signiture invalid!") #return false



def main():
    privkey = 'privatekey.pem'
    pubkey = 'publickey.pem'
    generate_private_key(privkey)
    generate_public_key(privkey, pubkey)

if __name__ == '__main__':
    main()
 



        

    


