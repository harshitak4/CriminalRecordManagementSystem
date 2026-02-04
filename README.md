# Criminal Record Management System (Advanced)

A distributed, blockchain-based system for managing criminal records with Authority handling.

## Features
- **Modular Architecture**: Clean separation of concerns (API, Blockchain, Crypto).
- **RSA Authority**: Private/Public key based record validation.
- **REST API**: Flask-based API for interacting with the blockchain.
- **Persistence**: Chains are saved to disk (`data/` directory).
- **Dynamic Configuration**: Nodes configured via `config/nodes.json`.

## Installation

1. Run the setup script to install dependencies and initialize directories:
   ```bash
   python setup.py
   ```

2. This will install:
   - flask
   - rsa
   - requests

## Usage

### Running a Node
Run a specific authority node by ID (0-4 defined in default config):

```bash
python main.py run --node-id 0
```
This will start Node 0 on port 5000 (default).

### Generating Keys
If keys are missing, they are auto-generated on first run. To manually generate:

```bash
python main.py gen-keys --node-id 0
```

### API Endpoints
- `GET /get_chain`: Retrieve the full blockchain.
- `GET /add_block`: Mine a new block.
- `POST /add_transaction`: Add a criminal record.
- `POST /verify_record`: Verify if a record exists in the chain.
- `POST /connect_node`: Connect to other peers.
- `GET /replace_chain`: Consensus algorithm to resolve conflicts.

## Project Structure
- `src/`: Source code.
- `config/`: Configuration files.
- `keys/`: RSA Keys.
- `data/`: Blockchain persistence.
- `legacy/`: Old implementation files.
