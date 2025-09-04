#!/usr/bin/env python3
"""
client_encode_encrypt_db.py - Encrypt the database
"""
import sys
import os
import numpy as np

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

# Add client library to path for Lattica imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../client/lattica_query_src'))

# from lattica_client import LatticaClient

def main():
    # Parse arguments
    size = int(sys.argv[1])
    
    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    dataset_dir = f"datasets/{instance_name}"
    encrypted_dir = f"io/{instance_name}/encrypted"
    key_dir = f"io/{instance_name}/keys"
    os.makedirs(encrypted_dir, exist_ok=True)
    
    # Load the combined database
    db = np.fromfile(f"{dataset_dir}/combined_db.bin", dtype=np.float32)
    print(f"Loaded {len(db)} float32 values from combined database")
    
    # Load context and secret key from step 3
    with open(f"{key_dir}/context.bin", "rb") as f:
        context = f.read()
    
    import json
    with open(f"{key_dir}/sk.json", "r") as f:
        sk_data = json.load(f)
    
    # Convert back from base64
    import base64
    secret_key = (
        base64.b64decode(sk_data[0]),
        base64.b64decode(sk_data[1])
    )
    
    # Serialize the plaintext data properly for FHE encryption
    import torch
    from lattica_query.serialization.api_serialization_utils import dumps_proto_tensor
    
    # Convert numpy array to PyTorch tensor and serialize properly
    db_tensor = torch.from_numpy(db)
    serialized_pt = dumps_proto_tensor(db_tensor)
    
    # Encrypt using Lattica toolkit
    import lattica_query.query_toolkit as toolkit_interface
    encrypted_data = toolkit_interface.enc(
        context, 
        secret_key, 
        serialized_pt,
        pack_for_transmission=True
    )
    
    # Save encrypted database as single file (no batching needed for Lattica)
    encrypted_db_path = f"{encrypted_dir}/db.bin"
    with open(encrypted_db_path, "wb") as f:
        f.write(encrypted_data)
    
    print(f"Encrypted database saved to {encrypted_db_path}")
    print(f"Encrypted size: {len(encrypted_data)} bytes")
    
if __name__ == "__main__":
    main()
