import hashlib
import json
import sqlite3
from typing import Dict, Any

DB_PATH = "roadsense.db"

class BlockchainLedger:
    """
    Implements a simple local blockchain structure to immutably audit maintenance records,
    budgets, and contractor activities.
    """
    
    @staticmethod
    def get_last_block() -> Dict[str, Any]:
        """Fetch the most recent block from the chain."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blockchain_ledger ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return {"block_hash": "0"}  # Genesis
        
    @staticmethod
    def add_audit_record(transaction_type: str, payload: Dict[str, Any]) -> str:
        """Adds a new block/record to the ledger by hashing the previous block."""
        last_block = BlockchainLedger.get_last_block()
        previous_hash = last_block['block_hash']
        
        # Simple Proof of Concept hashing
        payload_str = json.dumps(payload, sort_keys=True)
        combo = f"{previous_hash}{transaction_type}{payload_str}"
        new_hash = hashlib.sha256(combo.encode()).hexdigest()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO blockchain_ledger (block_hash, previous_hash, transaction_type, payload, nonce) VALUES (?, ?, ?, ?, ?)',
            (new_hash, previous_hash, transaction_type, payload_str, 0)
        )
        conn.commit()
        conn.close()
        
        return new_hash

    @staticmethod
    def verify_chain_integrity() -> bool:
        """Iterates over the blockchain and checks if hashes map validly. Ensures immutability."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blockchain_ledger ORDER BY id ASC")
        blocks = cursor.fetchall()
        conn.close()
        
        for i in range(1, len(blocks)):
            prev = blocks[i-1]
            curr = blocks[i]
            
            # Recreate hash
            combo = f"{prev['block_hash']}{curr['transaction_type']}{curr['payload']}"
            expected_hash = hashlib.sha256(combo.encode()).hexdigest()
            
            if curr['block_hash'] != expected_hash:
                return False  # Alteration detected
                
        return True
