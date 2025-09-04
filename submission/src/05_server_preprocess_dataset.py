#!/usr/bin/env python3
"""
server_preprocess_dataset.py - Upload encrypted database to server
"""
import sys
import os

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

# from lattica_client import LatticaClient

def main():
    # Parse arguments
    size = int(sys.argv[1])
    
    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    encrypted_dir = f"io/{instance_name}/encrypted"
    
    # TODO: Upload encrypted DB to server
    # with open(f"{encrypted_dir}/db.bin", "rb") as f:
    #     serialized_db = f.read()
    # 
    # worker_api.upload_similarity_db(serialized_db)
    
    # This step might be minimal for your SaaS implementation
    # since the DB is already uploaded/stored on the server
    
if __name__ == "__main__":
    main()
