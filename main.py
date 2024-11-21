import datetime
import hashlib
import json
import rsa

class KeyGeneration:
    def generateKeys(self):
        for i in range(5):
            public_key, private_key = rsa.newkeys(512)
            with open("Authorities_Public_Keys/"+f"Authority_{i}_PublicKey.pem", 'wb') as f:
                f.write(public_key.save_pkcs1("PEM"))
            with open(f"Authority_{i}_PrivateKey.pem", 'wb') as f:
                f.write(private_key.save_pkcs1("PEM"))

class Blockchain:
    def __init__(self):
        self.fp = open("KeyLedger.json", "r")
        self.chain = json.load(self.fp)
        self.wfp = open("KeyLedger.json", "w")

    def create_block(self, proof1, proof2, previous_hash):
        block = {'index': len(self.chain["blocks"]) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof1': proof1,
                 'proof2': proof2,
                 'previous_hash': previous_hash
                 }
        self.chain["blocks"].append(block)
        return block

    def get_previous_block(self):
        return self.chain["blocks"][-1]

    def hash_block(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = self.chain["blocks"][0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_block = block
            block_index += 1
        return True

    def addBlock(self, node, i):
        with open("Authorities_Public_Keys/"+f"Authority_{i}_PublicKey.pem", "rb") as f:
            publickey = rsa.PublicKey.load_pkcs1(f.read())
        with open(f"Authority_{i}_PrivateKey.pem", "rb") as f:
            privatekey = rsa.PrivateKey.load_pkcs1(f.read())
        proof1 = hashlib.sha256(str(publickey).encode()).hexdigest()
        proof2 = hashlib.sha256(
            (str(publickey)+str(privatekey)+node).encode()).hexdigest()
        if len(self.chain["blocks"]) == 0:
            previous_hash = '0'
            self.create_block(proof1, proof2, previous_hash)
        elif len(self.chain["blocks"]) > 0:
            prv_block = self.get_previous_block()
            previous_hash = self.hash_block(prv_block)
            self.create_block(proof1, proof2, previous_hash)

        if self.is_chain_valid(self.chain):
            print("ALL GOOD")
        else:
            print("Problem Detected")


if __name__ == '__main__':
    keyGeneration = KeyGeneration()
    keyGeneration.generateKeys()
    keyLedger = Blockchain()
    with open("nodes.json", "r") as rd:
        nodes = json.load(rd)
    for i in range(5):
        keyLedger.addBlock(nodes["nodes"][i], i)
    json.dump(keyLedger.chain, keyLedger.wfp, indent=4)
