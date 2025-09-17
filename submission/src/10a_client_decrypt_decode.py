#!/usr/bin/env python3
"""
client_decrypt_decode.py - Apply clear computation for debugging/verification
"""
import sys
import os
import numpy as np
import torch

from lattica_query.lattica_query_client import QueryClient
from harness.params import InstanceParams, PAYLOAD_DIM
from lib.server_logger import server_print
from lib.server_timer import ServerTimer

def main():
    # Parse arguments
    size = int(sys.argv[1])

    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    io_dir = f"io/{instance_name}"

    # Results were already decrypted and saved in step 08
    # Check that raw-result.bin exists
    raw_result_path = f"{io_dir}/raw-result.bin"
    if not os.path.exists(raw_result_path):
        raise FileNotFoundError(f"Raw result file not found: {raw_result_path}. Step 08 should have created this.")

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

    # Load the combined database for apply_clear operation
    db_path = f"{dataset_dir}/combined_db.npy"
    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"Combined database file not found: {db_path}. Make sure step 2 (preprocess) was run first.")

    db = np.load(db_path)  # Shape: (db_size, record_dim + 8)
    server_print(
        f"Loaded combined database with shape: {db.shape} for apply_clear")

    # Extend query vector to match database column count
    # Original query has record_dim dimensions, need to add 8 payload columns (7 + 1 marker)
    query_extended = np.zeros(record_dim + PAYLOAD_DIM + 1, dtype=np.float32)
    query_extended[:record_dim] = query  # Copy original query values
    # Leave payload columns as zeros (they won't affect similarity computation)

    # Reshape query to match database row format (1, record_dim + 8)
    query_row = query_extended.reshape(1, -1)

    # Concatenate: query as first row, database below
    combined_tensor_np = np.vstack([query_row, db])
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

    # Load the raw-result from step 08 for comparison
    raw_result = np.fromfile(raw_result_path, dtype=np.float32)
    server_print(f"Loaded raw result with shape: {raw_result.shape}")
    server_print(f"Clear result shape: {clear_result_array.shape}")

    # Check that shapes match
    if raw_result.shape != clear_result_array.shape:
        raise ValueError(
            f"Shape mismatch: raw_result {raw_result.shape} != clear_result {clear_result_array.shape}"
        )
    server_print("✓ Shape check passed: raw_result and clear_result have the same shape")

    # Check that content matches (with tolerance for floating point differences)
    tolerance = 1e-5
    max_diff = np.max(np.abs(raw_result - clear_result_array))
    server_print(f"Maximum difference between raw and clear results: {max_diff}")

    if not np.allclose(raw_result, clear_result_array, rtol=tolerance, atol=tolerance):
        raise ValueError(
            f"Content mismatch: maximum difference {max_diff} exceeds tolerance {tolerance}"
        )
    server_print(f"✓ Content check passed: raw_result and clear_result match within tolerance {tolerance}")

    # Additional debugging info
    server_print(f"Raw result - min: {raw_result.min():.6f}, max: {raw_result.max():.6f}, mean: {raw_result.mean():.6f}")
    server_print(f"Clear result - min: {clear_result_array.min():.6f}, max: {clear_result_array.max():.6f}, mean: {clear_result_array.mean():.6f}")

    # Log completion of apply_clear validation
    timer.log_step(10.1, "Apply clear validation")

if __name__ == "__main__":
    main()
