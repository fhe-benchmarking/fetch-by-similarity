#!/usr/bin/env python3
"""
client_preprocess_dataset.py - Merge db.bin and payloads.bin into combined_db.bin
"""
import sys
import os
import numpy as np

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

def main():
    # Parse arguments
    size = int(sys.argv[1])
    
    # Define paths based on size
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    dataset_dir = f"datasets/{instance_name}"
    
    # Get instance parameters for dimensions
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../harness'))
    from params import InstanceParams, PAYLOAD_DIM
    params = InstanceParams(size)
    db_size = params.get_db_size()
    record_dim = params.get_record_dim()
    
    # Read database vectors (float32)
    db = np.fromfile(f"{dataset_dir}/db.bin", dtype=np.float32)
    db = db.reshape((db_size, record_dim))
    
    # Read payload vectors (int16) 
    payloads = np.fromfile(f"{dataset_dir}/payloads.bin", dtype=np.int16)
    payloads = payloads.reshape((db_size, PAYLOAD_DIM))
    
    # Add marker value (4095) to each payload to make it 8 int16 values
    marker = np.full((db_size, 1), 4095, dtype=np.int16)
    extended_payloads = np.concatenate([payloads, marker], axis=1)
    
    # Convert everything to float32 for consistency and concatenate
    db_float32 = db.astype(np.float32)
    payloads_float32 = extended_payloads.astype(np.float32)
    
    # Combine: each record = [float32 vector] + [8 float32 payload values]
    combined = np.concatenate([db_float32, payloads_float32], axis=1)
    
    # Save combined database
    combined.tofile(f"{dataset_dir}/combined_db.bin")
    
    print(f"Merged {db_size} records into {dataset_dir}/combined_db.bin")
    print(f"Record format: {record_dim} vector dims + {PAYLOAD_DIM+1} payload values")
    
if __name__ == "__main__":
    main()
