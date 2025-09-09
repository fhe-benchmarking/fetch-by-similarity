#!/usr/bin/env python3
"""
client_encode_encrypt_db.py - Encrypt and upload the database
"""
import sys
import os
import numpy as np

from lib.server_logger import server_print
from lib.server_timer import ServerTimer
from lib.constants import MODEL_ID
from lib.similarity_upload import SimilarityUploader

def main():
    # Initialize timer for logging (at the very start to capture all operations)
    timer = ServerTimer()
    
    # Parse arguments
    size = int(sys.argv[1])
    
    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    dataset_dir = f"datasets/{instance_name}"
    encrypted_dir = f"io/{instance_name}/encrypted"
    key_dir = f"io/{instance_name}/keys"
    server_dir = f"io/{instance_name}/server"
    os.makedirs(encrypted_dir, exist_ok=True)
    
    # Load the combined database in 2D shape
    db = np.load(f"{dataset_dir}/combined_db.npy")
    server_print(f"Loaded combined database with shape: {db.shape}")
    
    # Load context, secret key, and homseq from step 3
    with open(f"{key_dir}/context.bin", "rb") as f:
        context = f.read()
    
    with open(f"{key_dir}/homseq.bin", "rb") as f:
        homseq = f.read()
    
    import json
    with open(f"{key_dir}/sk.json", "r") as f:
        sk_data = json.load(f)
    
    # Convert back from base64
    import base64
    secret_key = (
        base64.b64decode(sk_data[0]),
        base64.b64decode(sk_data[1])
    )
    
    # Parse homseq to extract pt_axis_external from client blocks
    from lattica_query.serialization.hom_op_pb2 import QueryClientSequentialHomOp
    homseq_proto = QueryClientSequentialHomOp()
    homseq_proto.ParseFromString(homseq)
    
    server_print(f"Parsed homseq with {len(homseq_proto.client_blocks)} client blocks")
    
    # Get pt_axis_external from the first client block if it exists
    first_block = homseq_proto.client_blocks[0]
    pt_axis_external = first_block.pt_axis_external if first_block.HasField("pt_axis_external") else None
    server_print(f"Found pt_axis_external field with value: {pt_axis_external}")
    pt_axis_external = 0  # Override to 0 for database encryption

    # Serialize the plaintext data properly for FHE encryption
    import torch
    from lattica_query.serialization.api_serialization_utils import dumps_proto_tensor
    
    server_print("Converting numpy array to PyTorch tensor...")
    # Convert numpy array to PyTorch tensor and serialize properly
    db_tensor = torch.from_numpy(db)
    server_print(f"Created tensor with shape: {db_tensor.shape}")
    
    server_print("Serializing tensor...")
    serialized_pt = dumps_proto_tensor(db_tensor)
    server_print(f"Serialized tensor size: {len(serialized_pt)} bytes")
    
    # Encrypt using Lattica toolkit
    import lattica_query.query_toolkit as toolkit_interface
    server_print(f"Starting encryption with pt_axis_external={pt_axis_external}...")
    encrypted_data = toolkit_interface.enc(
        context, 
        secret_key, 
        serialized_pt,
        pack_for_transmission=True,
        n_axis_external=pt_axis_external
    )
    server_print("Encryption completed")
    
    # Save encrypted database as single file (no batching needed for Lattica)
    encrypted_db_path = f"{encrypted_dir}/db.bin"
    with open(encrypted_db_path, "wb") as f:
        f.write(encrypted_data)
    
    server_print(f"Encrypted database saved to {encrypted_db_path}")
    server_print(f"Encrypted size: {len(encrypted_data)} bytes")
    
    # Log encryption phase completion
    timer.log_step(0, "Database encryption")
    
    # Upload encrypted database to Lattica
    token_path = f"{server_dir}/token.txt"
    if not os.path.exists(token_path):
        raise FileNotFoundError(f"Token file not found: {token_path}. Make sure step 3 (key generation) was run first.")
    
    with open(token_path, "r") as f:
        token = f.read().strip()
    
    server_print(f"Uploading encrypted database from {encrypted_db_path}...")
    
    uploader = SimilarityUploader(token)
    result = uploader.upload_database(encrypted_db_path, MODEL_ID)
    
    server_print(f"Database upload successful!")
    server_print(f"S3 Key: {result.get('s3Key')}")
    
    # Log upload phase completion
    timer.log_step(1, "Database upload")
    
if __name__ == "__main__":
    main()
