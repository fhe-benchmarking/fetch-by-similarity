#!/usr/bin/env python3
"""
server_preprocess_dataset.py - Upload encrypted database to server
"""
import sys
import os

from lib.constants import MODEL_ID
from lib.similarity_upload import SimilarityUploader
from lattica_query.worker_api import LatticaWorkerAPI

def main():
    # Parse arguments
    size = int(sys.argv[1])
    
    # Define paths
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    encrypted_dir = f"io/{instance_name}/encrypted"
    server_dir = f"io/{instance_name}/server"
    
    # Read the token saved from step 3
    token_path = f"{server_dir}/token.txt"
    if not os.path.exists(token_path):
        raise FileNotFoundError(f"Token file not found: {token_path}. Make sure step 3 (key generation) was run first.")
    
    with open(token_path, "r") as f:
        token = f.read().strip()
    
    # Upload encrypted database to Lattica
    db_path = f"{encrypted_dir}/db.bin"
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Encrypted database not found: {db_path}. Make sure step 4 (database encryption) was run first.")
    
    print(f"Uploading encrypted database from {db_path}...")
    
    uploader = SimilarityUploader(token)
    result = uploader.upload_database(db_path, MODEL_ID)
    
    print(f"Database upload successful!")
    print(f"Filename: {result.get('filename')}")
    print(f"S3 Key: {result.get('s3Key')}")
    
    # Load the database into the worker
    print("Loading database into worker...")
    worker_api = LatticaWorkerAPI(token)
    
    # Call load_similarity_database action with the filename
    filename = result.get('filename')
    worker_api.http_client.send_multipart_request(
        "load_similarity_database",
        action_params={"fake": "at least one param is required"},
        with_polling=True
    )
    
    print("Database loaded into worker successfully!")
    
if __name__ == "__main__":
    main()
