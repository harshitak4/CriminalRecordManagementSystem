# Criminal Record Management System - Usage Guide

This document provides a comprehensive guide on how the system works and how to operate it comfortably.

## System Overview

This is a **Proof of Authority (PoA)** blockchain implementation designed for managing criminal records. Unlike Proof of Work (Bitcoin), PoA relies on a set of trusted validators ("Authorities") who are authorized to validate transactions and mine blocks.

### Key Concepts
- **Authorities**: Trusted nodes (ID 0-4) that hold RSA Private Keys to sign blocks.
- **Ledger**: A distributed JSON file (`data/chain_X.json`) maintaining the history of records.
- **Zero-Knowledge-like Verification**: You can verify if a record exists using a Unique ID (UID) without exposing the entire database.

---

## 1. Initial Setup

Before running the system, ensure you have Python installed.

1.  **Install Dependencies & Initialize**:
    Run the setup script to download libraries and create necessary folders (`keys`, `data`, `logs`).
    ```bash
    python setup.py
    ```

2.  **Generate Keys**:
    The system uses RSA keys for identity. These are automatically generated on first run, but you can force generation:
    ```bash
    python main.py gen-keys
    ```
    *Check the `keys/` directory to see the generated `.pem` files.*

---

## 2. Running a Network

To simulate a distributed network, you should run multiple nodes (authorities) on different ports. Open separate terminal windows for each node.

### Terminal 1 (Authority 0)
```bash
python main.py run --node-id 0
```
*Runs on http://127.0.0.1:5000*

### Terminal 2 (Authority 1)
```bash
python main.py run --node-id 1
```
*Runs on http://127.0.0.1:5001*

---

## 3. Connecting Nodes

Nodes need to know about each other to sync the blockchain.

**Endpoint**: `POST /connect_node`

**Example (Connect Node 0 to Node 1):**
Use Postman or curl to tell Node 0 about Node 1.

```bash
curl -X POST http://127.0.0.1:5000/connect_node -H "Content-Type: application/json" -d '{"nodes": ["127.0.0.1:5001"]}'
```

---

## 4. Managing Records (Transactions)

### Add a Criminal Record
To add a record, you send a transaction. It enters a "pending" state until a block is mined.

**Endpoint**: `POST /add_transaction`

**Payload:**
```json
{
    "uid": "1234567890",
    "name": "John Doe",
    "pid": "P99",
    "court_id": "C-101",
    "district": "New York",
    "section": "302",
    "state": "NY"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/add_transaction -H "Content-Type: application/json" -d "{\"uid\": \"12345\", \"name\": \"Bad Guy\", \"pid\": \"P01\", \"court_id\": \"C01\", \"district\": \"Dist1\", \"section\": \"Sec1\", \"state\": \"State1\"}"
```

### Mine a Block
Pending transactions are confirmed and added to the blockchain when a block is mined.

**Endpoint**: `GET /add_block`

**Example:**
```bash
curl http://127.0.0.1:5000/add_block
```

---

## 5. Verification & Syncing

### Verify a Record
Check if a criminal record exists on the blockchain using just the UID.

**Endpoint**: `POST /verify_record`

**Payload:**
```json
{ "uid": "12345" }
```

### Sync Chains (Consensus)
If Node 1 has a longer chain than Node 0, Node 0 needs to update its ledger.

**Endpoint**: `GET /replace_chain`

**Example:**
```bash
curl http://127.0.0.1:5000/replace_chain
```

---

## Troubleshooting

- **500 Error**: Check if `keys/` contains the private key for the node ID you are running.
- **Port already in use**: Ensure you aren't trying to run two nodes with the same ID or on the same port.
- **Connection Refused**: Ensure the other node you are connecting to is actually running.
