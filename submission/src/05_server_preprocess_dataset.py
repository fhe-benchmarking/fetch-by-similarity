#!/usr/bin/env python3
"""
server_preprocess_dataset.py - Upload encrypted database to server
"""
import sys
import os

from lattica_query.worker_api import LatticaWorkerAPI
from lib.server_logger import server_print

def main():
    # Parse arguments
    size = int(sys.argv[1])
    
    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    server_dir = f"io/{instance_name}/server"

    # Read the token saved from step 3
    token_path = f"{server_dir}/token.txt"
    if not os.path.exists(token_path):
        raise FileNotFoundError(f"Token file not found: {token_path}. Make sure step 3 (key generation) was run first.")
    
    with open(token_path, "r") as f:
        token = f.read().strip()
    
    # Load the database into the worker (database was uploaded in step 4)
    server_print("Loading database into worker...")
    worker_api = LatticaWorkerAPI(token)
    
    # Call load_custom_encrypted_data action
    worker_api.http_client.send_multipart_request(
        "load_custom_encrypted_data",
        action_params={"fake": "at least one param is required"}
    )
    
    server_print("Database loaded into worker successfully!")
    
if __name__ == "__main__":
    main()
