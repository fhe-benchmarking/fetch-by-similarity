#!/usr/bin/env python3
"""
client_encode_encrypt_query.py - Encrypt the query vector
"""
import sys
import os
import numpy as np

# No path manipulation needed with proper package structure

# from lattica_client import LatticaClient

def main():
    # Parse arguments
    size = int(sys.argv[1])
    
    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    dataset_dir = f"datasets/{instance_name}"
    encrypted_dir = f"io/{instance_name}/encrypted"
    
    # TODO: Read and encrypt query
    # query = np.fromfile(f"{dataset_dir}/query.bin", dtype=np.float32)
    # encrypted_query = toolkit.enc(query)
    # with open(f"{encrypted_dir}/query.bin", "wb") as f:
    #     f.write(encrypted_query)
    
    # Create placeholder for now (remove in real implementation)
    open(f"{encrypted_dir}/query.bin", 'wb').close()
    
if __name__ == "__main__":
    main()
