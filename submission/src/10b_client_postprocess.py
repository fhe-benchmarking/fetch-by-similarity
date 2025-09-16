#!/usr/bin/env python3
"""
client_postprocess.py - Post-process decrypted results - convert payload back from float64 to int16.
"""
import sys
import os
import numpy as np

from harness.params import PAYLOAD_DIM

def extract_count(raw_results):
    """Extract count from decrypted results."""
    # In count-only mode, the file contains just the count value
    return int(raw_results[0])

def extract_payloads(raw_results):
    """Extract payload vectors from decrypted results and convert float64 to int16."""
    # In full mode, the file contains only payload data (no count)
    n_matches = len(raw_results) // PAYLOAD_DIM
    
    if n_matches == 0:
        return np.array([], dtype=np.int16).reshape(0, PAYLOAD_DIM)
    
    # Reshape and convert back to int16
    payloads_float = raw_results[:n_matches * PAYLOAD_DIM].reshape(n_matches, PAYLOAD_DIM)
    
    # Check for invalid values before conversion
    if not np.all(np.isfinite(payloads_float)):
        bad_vals = payloads_float[~np.isfinite(payloads_float)]
        raise ValueError(f"Invalid float values in raw results: {bad_vals[:5]}...")
    
    payloads_int16 = np.round(payloads_float).astype(np.int16)
    
    return payloads_int16

def main():
    # Parse arguments
    size = int(sys.argv[1])
    count_only = len(sys.argv) > 2 and sys.argv[2] == "--count_only"
    
    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    io_dir = f"io/{instance_name}"
    
    # Read raw results as float64 (the actual dtype saved by step 8)
    raw_results = np.fromfile(f"{io_dir}/raw-result.bin", dtype=np.float64)
    print(f"Loaded raw_results shape: {raw_results.shape}")
    print(f"Loaded raw_results dtype: {raw_results.dtype}")
    print(f"First 10 values: {raw_results[:10] if len(raw_results) >= 10 else raw_results}")

    if count_only:
        # Extract count and save as np.int_ (system-dependent integer size)
        count = extract_count(raw_results)
        np.array([count], dtype=np.int_).tofile(f"{io_dir}/results.bin")
    else:
        # Extract payload vectors, convert to int16, sort lexicographically, and save
        payloads = extract_payloads(raw_results)  # Shape: (n_matches, PAYLOAD_DIM)
        
        if len(payloads) > 0:
            # Sort lexicographically (sort by columns from right to left)
            sorted_payloads = payloads[np.lexsort(payloads.T[::-1])]
        else:
            sorted_payloads = payloads
        
        sorted_payloads.tofile(f"{io_dir}/results.bin")
    
if __name__ == "__main__":
    main()
