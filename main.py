import argparse
import json
import os
import sys
from src.api import create_app
from src.crypto_utils import CryptoUtils

def load_config():
    config_path = "config/nodes.json"
    if not os.path.exists(config_path):
        print("Config file not found in config/nodes.json")
        sys.exit(1)
    with open(config_path, "r") as f:
        return json.load(f)

def run_node(node_id, port):
    print(f"Starting Node {node_id} on port {port}")
    config = load_config()
    
    peers = []
    for node in config["nodes"]:
        if node["id"] != node_id:
            peers.append(f"{node['host']}:{node['port']}")
            
    app = create_app(node_id, port, peers)
    app.run(host='0.0.0.0', port=port)

def generate_keys(node_id=None):
    if node_id is not None:
        print(f"Generating keys for Node {node_id}")
        CryptoUtils.generate_keys(node_id, key_dir="keys")
    else:
        print("Generating keys for all nodes in config...")
        config = load_config()
        for node in config["nodes"]:
            print(f"Generating keys for Node {node['id']}")
            CryptoUtils.generate_keys(node['id'], key_dir="keys")

def main():
    parser = argparse.ArgumentParser(description="Criminal Record Management System Node")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run a blockchain node")
    run_parser.add_argument("--node-id", type=int, required=True, help="Node ID (0-4)")
    run_parser.add_argument("--port", type=int, help="Port to run on (overrides config)")

    gen_keys_parser = subparsers.add_parser("gen-keys", help="Generate RSA keys")
    gen_keys_parser.add_argument("--node-id", type=int, help="Specific node ID (optional)")

    args = parser.parse_args()

    if args.command == "run":
        config = load_config()
        port = args.port
        if not port:
            # Find port from config
            for node in config["nodes"]:
                if node["id"] == args.node_id:
                    port = node["port"]
                    break
        if not port:
            port = 5000 + args.node_id 
            
        # Ensure keys exist
        if not os.path.exists(f"keys/Authority_{args.node_id}_PrivateKey.pem"):
            print(f"Keys for node {args.node_id} not found. Generating...")
            CryptoUtils.generate_keys(args.node_id, key_dir="keys")
            
        run_node(args.node_id, port)
        
    elif args.command == "gen-keys":
        generate_keys(args.node_id)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
