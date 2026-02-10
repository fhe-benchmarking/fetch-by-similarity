"""
client_key_generation.py - Generate and save FHE keys
"""
import pickle
import sys
import lattica_query.query_toolkit as toolkit_interface
import submission_utils

local_file_paths, _ = submission_utils.init(sys.argv)

context = pickle.load(open(local_file_paths.PATH_CONTEXT, "rb"))
hom_seq = pickle.load(open(local_file_paths.PATH_HOM_SEQ, "rb"))

sk, ek = toolkit_interface.generate_key(hom_seq, context)

pickle.dump(ek, open(local_file_paths.PATH_EK, "wb"))
pickle.dump(sk, open(local_file_paths.PATH_SK, "wb"))
