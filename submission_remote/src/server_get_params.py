import sys
import pickle

import submission_utils
from lattica_query.auth import get_demo_token

local_file_paths, _ = submission_utils.init(sys.argv)


# Get access_token for public model
access_token = get_demo_token("similarityFetchToy")
pickle.dump(access_token, open(local_file_paths.PATH_ACCESS_TOKEN, "wb"))

# Get encryption params and model metadata from BE
client = submission_utils.get_lattica_client(local_file_paths)
context, hom_seq = client.get_init_data()

# Save data to local file system
pickle.dump(context, open(local_file_paths.PATH_CONTEXT, "wb"))
pickle.dump(hom_seq, open(local_file_paths.PATH_HOM_SEQ, "wb"))
