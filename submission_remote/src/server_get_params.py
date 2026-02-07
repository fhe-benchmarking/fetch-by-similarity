import sys
import pickle

import submission_utils
from lattica_query.auth import get_demo_token

local_file_paths, instance_params = submission_utils.init(sys.argv)

if instance_params.size == 0:
    # Get access_token for public model
    access_token = get_demo_token("similarityFetchToy")
    pickle.dump(access_token, open(local_file_paths.PATH_ACCESS_TOKEN, "wb"))
elif instance_params.size == 1:
    # Non-public model, use pre-shared access token. Note that if multiple users run at the same time they may interfere.
    access_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlIwRTR5Ujd2RnFNSW9ESTBrdGVlayJ9.eyJ0b2tlbklkIjoiZmQ0NTQzOTctNDMwMy00Yjg0LTliYzktNzVlZDZmNDgyM2RlIiwiaXNzIjoiaHR0cHM6Ly9sYXR0aWNhLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJtUWFORWR6R1pVd1o1TDVRSjlrNTFVOG91TjRHOTJicEBjbGllbnRzIiwiYXVkIjoiaHR0cHM6Ly9teWFwaS9hcGkiLCJpYXQiOjE3Njc4NzE4NzIsImV4cCI6MTc3MDQ2Mzg3Miwic2NvcGUiOiJ1c2VyIGRlZmF1bHQiLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJhenAiOiJtUWFORWR6R1pVd1o1TDVRSjlrNTFVOG91TjRHOTJicCIsInBlcm1pc3Npb25zIjpbInVzZXIiLCJkZWZhdWx0Il19.IHtiEoPIXOspUyA0jNSdW_2edxPmEOfPrXowunkdiqEg7kzyHaPaVW3bmyHe8gIfJ84fBSfqp4F98RlWShHUNcGKZdhGgtZhmqnf1Ie-YvJKpogfap7O5rrts4jx_a80DXVewXv_SfmK_hGSQw1tCzknjwGn3_vD16jLfRR3VqB9YA31dPLNCHZlq8o4xDEp2dPIMj5tmn9rzBq6IbpZqKzssXlGwTMn-x5LH4YI9cmitaAOuD4_hlUz8WXzdz4Bur-DyatBg6OSvVa3KDTbwMyaQEHnKop9XksYBLM1c4d6TxZ71MYDG1g5R9n00Mj-Kw_iiCFpj9nsIAKipmFiGg"
    pickle.dump(access_token, open(local_file_paths.PATH_ACCESS_TOKEN, "wb"))
else:
    raise ValueError("Submission is publicly available only for SIZE=0 or SIZE=1, for other sizes please contact hello@lattica.ai.")


# Get encryption params and model metadata from BE
client = submission_utils.get_lattica_client(local_file_paths)
context, hom_seq = client.get_init_data()

# Save data to local file system
pickle.dump(context, open(local_file_paths.PATH_CONTEXT, "wb"))
pickle.dump(hom_seq, open(local_file_paths.PATH_HOM_SEQ, "wb"))
