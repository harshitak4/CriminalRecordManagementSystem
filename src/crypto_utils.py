import hashlib
import rsa
import json
import os

class CryptoUtils:
    @staticmethod
    def generate_keys(node_id, key_dir="keys"):
        public_key, private_key = rsa.newkeys(512)
        
        pub_path = os.path.join(key_dir, f"Authority_{node_id}_PublicKey.pem")
        priv_path = os.path.join(key_dir, f"Authority_{node_id}_PrivateKey.pem")
        
        with open(pub_path, 'wb') as f:
            f.write(public_key.save_pkcs1("PEM"))
            
        with open(priv_path, 'wb') as f:
            f.write(private_key.save_pkcs1("PEM"))
            
    @staticmethod
    def load_keys(node_id, key_dir="keys"):
        pub_path = os.path.join(key_dir, f"Authority_{node_id}_PublicKey.pem")
        priv_path = os.path.join(key_dir, f"Authority_{node_id}_PrivateKey.pem")
        
        if not os.path.exists(pub_path) or not os.path.exists(priv_path):
            raise FileNotFoundError(f"Keys for node {node_id} not found in {key_dir}")
            
        with open(pub_path, 'rb') as f:
            public_key = rsa.PublicKey.load_pkcs1(f.read())
            
        with open(priv_path, 'rb') as f:
            private_key = rsa.PrivateKey.load_pkcs1(f.read())
            
        return public_key, private_key

    @staticmethod
    def hash_block(block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    @staticmethod
    def sign_data(data, private_key):
        return hashlib.sha256(str(rsa.sign(str(data).encode(), private_key, 'SHA-256')).encode()).hexdigest()
