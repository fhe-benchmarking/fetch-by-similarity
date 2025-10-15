#!/usr/bin/env python3
"""
client_decrypt_decode.py - Decrypt homomorphic computation results and optionally apply clear computation for debugging/verification
"""
import sys
import os
import numpy as np
import torch
import json
import base64

from lattica_query.lattica_query_client import QueryClient
from lattica_query.serialization.api_serialization_utils import load_proto_tensor
import lattica_query.query_toolkit as toolkit_interface
from harness.params import InstanceParams
from lib.server_logger import server_print
from lib.server_timer import ServerTimer

def main():
    # Parse arguments
    size = int(sys.argv[1])

    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    io_dir = f"io/{instance_name}"
    encrypted_dir = f"{io_dir}/encrypted"
    key_dir = f"{io_dir}/keys"
    server_dir = f"{io_dir}/server"

    # Initialize timer for logging
    timer = ServerTimer()

    # Load encrypted result from step 9
    encrypted_result_path = f"{encrypted_dir}/results.bin"
    if not os.path.exists(encrypted_result_path):
        raise FileNotFoundError(f"Encrypted results not found: {encrypted_result_path}. Make sure step 9 was run first.")
    server_print(f"Loading encrypted results from {encrypted_result_path}")
    with open(encrypted_result_path, "rb") as f:
        serialized_ct_res = f.read()

    # Load context and secret key for decryption
    context_path = f"{key_dir}/context.bin"
    sk_path = f"{key_dir}/sk.json"

    if not os.path.exists(context_path):
        raise FileNotFoundError(f"Context file not found: {context_path}. Make sure step 3 (key generation) was run first.")
    if not os.path.exists(sk_path):
        raise FileNotFoundError(f"Secret key file not found: {sk_path}. Make sure step 3 (key generation) was run first.")

    # Load context
    with open(context_path, "rb") as f:
        context = f.read()

    # Load secret key (decode from base64 JSON format)
    with open(sk_path, "r") as f:
        sk_data = json.load(f)

    secret_key = (
        base64.b64decode(sk_data[0]),
        base64.b64decode(sk_data[1])
    )

    # Decrypt the results
    server_print("Decrypting results...")
    serialized_pt = toolkit_interface.dec(
        context,
        secret_key,
        serialized_ct_res,
        as_complex=False
    )
    timer.log_step(10.1, "Decrypt results")

    # Convert decrypted proto to tensor
    server_print("Converting decrypted result to tensor...")
    result_tensor = load_proto_tensor(serialized_pt)
    server_print(f"Result shape: {result_tensor.shape} and dtype: {result_tensor.dtype}")

    # Convert to numpy array and save
    result_array = result_tensor.numpy()
    server_print(f"Final result array shape: {result_array.shape} and dtype: {result_array.dtype}")

    # Save raw decrypted results
    raw_result_path = f"{io_dir}/raw-result.bin"
    result_array.tofile(raw_result_path)
    server_print(f"Raw results saved to {raw_result_path}")

    # Check if apply_clear is enabled via environment variable
    apply_clear_enabled = os.getenv('LATTICA_APPLY_CLEAR', '').lower() == 'true'
    if not apply_clear_enabled:
        server_print("LATTICA_APPLY_CLEAR not enabled, skipping clear computation validation")
        return

    server_print("LATTICA_APPLY_CLEAR enabled, running clear computation validation...")

    # Initialize timer for logging
    timer = ServerTimer()

    # Get instance parameters
    params = InstanceParams(size)
    record_dim = params.get_record_dim()
    db_size = params.get_db_size()

    # Additional paths needed for apply_clear
    dataset_dir = f"datasets/{instance_name}"
    server_dir = f"{io_dir}/server"

    # Load token for client initialization
    token_path = f"{server_dir}/token.txt"
    if not os.path.exists(token_path):
        raise FileNotFoundError(
            f"Token file not found: {token_path}. Make sure step 3 (key generation) was run first.")

    with open(token_path, "r") as f:
        token = f.read().strip()

    # Initialize QueryClient for apply_clear operation
    server_print("Initializing QueryClient for apply_clear...")
    if os.getenv('LATTICA_RUN_MODE') == 'LOCAL':
        from lattica_query.dev_utils.lattica_query_client_local import \
            LocalQueryClient
        client = LocalQueryClient(token)
    else:
        client = QueryClient(token)

    # Load the original query vector
    query_path = f"{dataset_dir}/query.bin"
    if not os.path.exists(query_path):
        raise FileNotFoundError(f"Query file not found: {query_path}.")

    query = np.fromfile(query_path, dtype=np.float32)
    server_print(f"Loaded query vector with shape: {query.shape}")

    # Load the database for apply_clear operation
    db_path = f"{dataset_dir}/db.npy"
    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"Database file not found: {db_path}. Make sure step 2 (preprocess) was run first.")

    db = np.load(db_path)  # Shape: (db_size, record_dim + 8)
    server_print(
        f"Loaded database with shape: {db.shape} for apply_clear")


    # Load the payloads for apply_clear operation
    payloads_path = f"{dataset_dir}/payloads.npy"
    if not os.path.exists(payloads_path):
        raise FileNotFoundError(
            f"Payloads file not found: {payloads_path}. Make sure step 2 (preprocess) was run first.")

    payloads = np.load(payloads_path)  # Shape: (db_size, record_dim + 8)
    server_print(
        f"Loaded payloads with shape: {payloads.shape} for apply_clear")


    query_tensor = torch.from_numpy(query)
    n_slots = 2**9
    query_tensor = query_tensor.expand(n_slots // record_dim, record_dim).reshape(n_slots)

    # Extend query vector to match database column count
    # Original query has record_dim dimensions, need to add 8 payload columns (7 + 1 marker)
    query_extended = np.zeros(db_size, dtype=np.float32)
    query_extended[:n_slots] = query_tensor  # Copy original query values
    # Leave payload columns as zeros (they won't affect similarity computation)

    # Reshape query to match database row format (1, record_dim + 8)
    query_row = query_extended.reshape(-1, 1)

    # Concatenate: query as first row, database below
    combined_tensor_np = np.hstack([query_row, db, payloads])
    server_print(
        f"Running apply clear on combined tensor with shape {combined_tensor_np.shape} (query + {db.shape[0]} db rows)")

    # Convert to PyTorch tensor for apply_clear
    combined_tensor = torch.from_numpy(combined_tensor_np)

    # Apply clear computation on combined tensor
    server_print("Running apply_clear computation...")
    try:
        clear_result_tensor = client.apply_clear(combined_tensor)
        server_print(f"Clear result shape: {clear_result_tensor.shape}")
    except Exception as e:
        server_print(f"ERROR: apply_clear failed with: {str(e)}")
        server_print(f"Skipping clear computation validation due to error")
        return

    # Save clear result for comparison/debugging
    clear_result_array = clear_result_tensor.numpy()
    clear_result_path = f"{io_dir}/clear-result.bin"
    clear_result_array.tofile(clear_result_path)
    server_print(f"Clear computation results saved to {clear_result_path}")

    # Log completion of apply_clear validation
    timer.log_step(10.1, "Apply clear validation")


if __name__ == "__main__":
    main()
