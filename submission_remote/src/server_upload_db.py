"""
server_preprocess_dataset.py - Upload database to server
"""
import sys
import submission_utils

local_file_paths, _ = submission_utils.init(sys.argv)
client = submission_utils.get_lattica_client(local_file_paths)
archive_path = local_file_paths.get_ct_upload_path("db_and_payloads_zip")
client.upload_custom_encrypted_data(archive_path)
