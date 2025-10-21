#!/usr/bin/env python3
"""
client_encode_encrypt_db.py - Encrypt and upload the database
"""
import sys
import os
import json
import base64
import numpy as np
import torch
import zipfile

from lib.server_logger import server_print
from lib.server_timer import ServerTimer
from lib.constants import MODEL_ID
from lib.similarity_upload import SimilarityUploader
from lattica_query.serialization.api_serialization_utils import dumps_proto_tensor
import lattica_query.query_toolkit as toolkit_interface

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
    
    # Load the db and payloads from step 2
    db_tensor = torch.from_numpy(np.load(f"{dataset_dir}/db.npy"))
    server_print(f"Loaded database with shape: {db_tensor.shape}")

    payloads_tensor = torch.from_numpy(np.load(f"{dataset_dir}/payloads.npy"))
    server_print(f"Loaded payloads with shape: {payloads_tensor.shape}")

    # Load context and secret key from step 3
    with open(f"{key_dir}/context.bin", "rb") as f:
        context = f.read()
    
    with open(f"{key_dir}/sk.json", "r") as f:
        sk_data = json.load(f)
    
    # Convert back from base64
    serialized_sk = (
        base64.b64decode(sk_data[0]),
        base64.b64decode(sk_data[1])
    )

    # Encrypt db using Lattica toolkit
    serialized_db_pt = dumps_proto_tensor(db_tensor)

    encrypted_db_data = toolkit_interface.enc(
        context, 
        serialized_sk, 
        serialized_db_pt,
        custom_state_name="db",
    )
    server_print(f"Encrypted db size: {len(encrypted_db_data)} bytes")
    timer.log_step(4.11, "Database encryption")

    # Encrypt payloads using Lattica toolkit
    serialized_payloads_pt = dumps_proto_tensor(payloads_tensor)

    encrypted_payloads_data = toolkit_interface.enc(
        context, 
        serialized_sk, 
        serialized_payloads_pt,
        custom_state_name="payload",
    )
    server_print(f"Encrypted payloads size: {len(encrypted_payloads_data)} bytes")
    timer.log_step(4.12, "Payloads encryption")

    # Get token for upload
    token_path = f"{server_dir}/token.txt"
    if not os.path.exists(token_path):
        raise FileNotFoundError(f"Token file not found: {token_path}. Make sure step 3 (key generation) was run first.")
    
    with open(token_path, "r") as f:
        token = f.read().strip()

    # Write archive containing db & payloads
    archive_path = f"{encrypted_dir}/encrypted_data.zip"
    with zipfile.ZipFile(archive_path, 'w') as zipf:
        zipf.writestr('db.bin', encrypted_db_data)
        zipf.writestr('payloads.bin', encrypted_payloads_data)
    server_print(f"db.bin & payloads.bin archive created successfully.")

    # Upload the archive as custom encrypted data
    server_print(f"Uploading encrypted database & payloads from {archive_path}...")
    uploader = SimilarityUploader(token)
    uploader.upload_database(archive_path, MODEL_ID)

    # Log upload phase completion
    timer.log_step(4.2, "Database & payloads upload")
    
if __name__ == "__main__":
    main()
