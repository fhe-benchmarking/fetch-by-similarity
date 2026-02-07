import pickle
import sys

from lattica_query.serialization.api_serialization_utils import load_proto_tensor
import lattica_query.query_toolkit as toolkit_interface

import submission_utils

local_file_paths, _ = submission_utils.init(sys.argv)

ct_res     = pickle.load(open(local_file_paths.get_ct_download_path("query"), "rb"))
context    = pickle.load(open(local_file_paths.PATH_CONTEXT, "rb"))
secret_key = pickle.load(open(local_file_paths.PATH_SK, "rb"))

serialized_res = toolkit_interface.dec(context, secret_key, ct_res,)
raw_result = load_proto_tensor(serialized_res)

pickle.dump(raw_result, open(local_file_paths.PATH_RAW_RESULT, "wb"))

