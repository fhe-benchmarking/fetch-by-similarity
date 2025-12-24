#!/usr/bin/env python3
"""
server_preprocess_dataset.py - Upload database to server
"""
import sys

from lib.server_logger import server_print
from lib.utils import get_query_client


def main():
    size = int(sys.argv[1])
    instance_names = ['toy', 'small', 'medium', 'large']
    instance_name = instance_names[size]
    encrypted_dir = f"io/{instance_name}/encrypted"
    archive_path = f"{encrypted_dir}/encrypted_data.zip"

    server_print(f"Uploading encrypted database & payloads from {archive_path}...")
    client = get_query_client()
    client.upload_custom_encrypted_data(archive_path)
    server_print("Database loaded into worker successfully!")


if __name__ == "__main__":
    main()
