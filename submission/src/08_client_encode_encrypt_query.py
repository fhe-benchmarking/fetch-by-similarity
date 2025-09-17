#!/usr/bin/env python3
"""
client_encode_encrypt_query.py - Run query using QueryClient
"""
import sys
import os
import numpy as np
import torch
import json
import base64

from lattica_query.lattica_query_client import QueryClient
from lattica_query.serialization.api_serialization_utils import dumps_proto_tensor
from harness.params import InstanceParams
from lib.server_logger import server_print
from lib.server_timer import ServerTimer

def main():

    # Parse arguments
    size = int(sys.argv[1])
    count_only = len(sys.argv) > 2 and sys.argv[2] == "--count_only"
    
    # Get instance parameters
    params = InstanceParams(size)
    record_dim = params.get_record_dim()
    
    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    dataset_dir = f"datasets/{instance_name}"
    io_dir = f"io/{instance_name}"
    key_dir = f"{io_dir}/keys"
    server_dir = f"{io_dir}/server"
    encrypted_dir = f"{io_dir}/encrypted"

    # Ensure directories exist
    os.makedirs(encrypted_dir, exist_ok=True)
    
    # Read the query vector
    query_path = f"{dataset_dir}/query.bin"
    if not os.path.exists(query_path):
        raise FileNotFoundError(f"Query file not found: {query_path}. Make sure the harness has generated the query.")
    
    query = np.fromfile(query_path, dtype=np.float32)
    server_print(f"Loaded query vector with shape: {query.shape}")
    
    # Load token from step 3
    token_path = f"{server_dir}/token.txt"
    if not os.path.exists(token_path):
        raise FileNotFoundError(f"Token file not found: {token_path}. Make sure step 3 (key generation) was run first.")
    
    with open(token_path, "r") as f:
        token = f.read().strip()
    
    # Load context, secret key, and homseq from step 3
    context_path = f"{key_dir}/context.bin"
    sk_path = f"{key_dir}/sk.json"
    homseq_path = f"{key_dir}/homseq.bin"
    
    if not os.path.exists(context_path):
        raise FileNotFoundError(f"Context file not found: {context_path}. Make sure step 3 (key generation) was run first.")
    if not os.path.exists(sk_path):
        raise FileNotFoundError(f"Secret key file not found: {sk_path}. Make sure step 3 (key generation) was run first.")
    if not os.path.exists(homseq_path):
        raise FileNotFoundError(f"Homseq file not found: {homseq_path}. Make sure step 3 (key generation) was run first.")
    
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
    
    # Load homseq
    with open(homseq_path, "rb") as f:
        homseq = f.read()

    timer = ServerTimer()
    # Convert query to PyTorch tensor
    server_print("Converting query vector to PyTorch tensor...")
    query_tensor = torch.from_numpy(query)
    server_print(f"Created tensor with shape: {query_tensor.shape}")
    n_slots = 2**9
    query_tensor = query_tensor.expand(n_slots // record_dim, record_dim).reshape(n_slots)
    timer.log_step(8.1, "Expand and reshape")
    server_print("Initializing QueryClient...")
    if os.getenv('LATTICA_RUN_MODE') == 'LOCAL':
        from lattica_query.dev_utils.lattica_query_client_local import \
            LocalQueryClient
        client = LocalQueryClient(token)
    else:
        client = QueryClient(token)
    server_print("Running homomorphic query computation...")

    try:
        result_tensor = client.run_query(
            context,
            secret_key,
            query_tensor,
            homseq,
            timing_report=False
        )
    except RuntimeError as e:
        server_print(f"Error during query computation: {e}")
        server_print(f"Expected shape might be different. Query tensor shape: {query_tensor.shape}")
        raise
    
    server_print(f"Result shape: {result_tensor.shape}")

    # Debug: Check tensor properties
    server_print(f"Result tensor dtype: {result_tensor.dtype}")

    # Log query computation phase completion
    timer.log_step(8.2, "Run Query")

    if result_tensor.is_complex():
        raise "got compolex tensor"

    result_array = result_tensor.numpy()
    server_print(f"Final result array shape: {result_array.shape}")
    server_print(f"Final result array dtype: {result_array.dtype}")

    # Save raw decrypted results (this would normally be done in step 10a)
    # The raw-result is in float32.
    raw_result_path = f"{io_dir}/raw-result.bin"
    result_array.tofile(raw_result_path)
    server_print(f"Raw results saved to {raw_result_path}")

if __name__ == "__main__":
    main()
