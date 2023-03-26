import hashlib
import secrets
import random
import time
import string

def hashData(data):
    string = ""
    if type(data) == list:
        for i in data:
            string += i
        hash = hashlib.sha256(string.encode()).hexdigest()
        return hash

    hash = hashlib.sha256(data.encode()).hexdigest()
    return hash

def hash_Input(zeros):
    attempts = 0
    str = ''
    found = False
    while not found:
        randomMessage = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(15))
        output = hashlib.sha256(randomMessage.encode())
        output = output.hexdigest()
        if output.startswith(zeros):
            return randomMessage, output

def main():
    numZeros = int(input("Please enter the amount of leading zeros: "))
    zeros = ""
    for i in range(numZeros): zeros += "0"
    randomMessage, hash = hash_Input(zeros)
    print(f"The message {randomMessage} generates the hash: {hash}")

if __name__ == "__main__":
    main()