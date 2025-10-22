#!/usr/bin/env python3
"""
client_preprocess_dataset.py - Adjust db.bin and payloads.bin as numpy files
"""
import sys
import numpy as np

from harness.params import InstanceParams, PAYLOAD_DIM
from lib.server_logger import server_print
from lib.constants import PRECISION

def main():
    # Parse arguments
    size = int(sys.argv[1])
    
    # Define paths based on size
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    dataset_dir = f"datasets/{instance_name}"
    
    # Get instance parameters for dimensions
    params = InstanceParams(size)
    db_size = params.get_db_size()
    record_dim = params.get_record_dim()
    
    # Read database vectors (float32)
    db = np.fromfile(f"{dataset_dir}/db.bin", dtype=np.float32)
    db = db.reshape((db_size, record_dim))

    # Read payload vectors (int16) 
    payloads = np.fromfile(f"{dataset_dir}/payloads.bin", dtype=np.int16)
    payloads = payloads.reshape((db_size, PAYLOAD_DIM))

    # Add marker value (8192) to each payload to make it 8 int16 values
    marker = np.full((db_size, 1), 8192, dtype=np.int16)
    extended_payloads = np.concatenate([marker, payloads], axis=1)
    extended_payloads = extended_payloads / PRECISION

    # Save combined database preserving 2D shape
    np.save(f"{dataset_dir}/db.npy", db)
    np.save(f"{dataset_dir}/payloads.npy", extended_payloads)
    
    server_print(f"Database shape: {db.shape} ({record_dim} vector dims")
    server_print(f"Extended payloads shape: {extended_payloads.shape} ({PAYLOAD_DIM+1} payload values per record)")

    
if __name__ == "__main__":
    main()
