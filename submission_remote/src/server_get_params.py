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
    access_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlIwRTR5Ujd2RnFNSW9ESTBrdGVlayJ9.eyJ0b2tlbklkIjoiNzA1MmY0YTctNDFmYi00OWNhLWIwMTMtMTcwYjlhMzhjODJhIiwiaXNzIjoiaHR0cHM6Ly9sYXR0aWNhLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJtUWFORWR6R1pVd1o1TDVRSjlrNTFVOG91TjRHOTJicEBjbGllbnRzIiwiYXVkIjoiaHR0cHM6Ly9teWFwaS9hcGkiLCJpYXQiOjE3NzA2MjgxNjAsImV4cCI6MTc3MzIyMDE2MCwic2NvcGUiOiJ1c2VyIGRlZmF1bHQiLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJhenAiOiJtUWFORWR6R1pVd1o1TDVRSjlrNTFVOG91TjRHOTJicCIsInBlcm1pc3Npb25zIjpbInVzZXIiLCJkZWZhdWx0Il19.Yz5-_LiSN_955-6t12-fQcBjyxNen3Df0Ec_Tj98AIZctnUegj7xX4ZdhL9vi1QZd2KhYXGkoy8QCqfZVJ8z9_u1p-CQfvz2rA2EwdhPxIgz6VhUlUoaMjXnVXm1jI0liKWco9pahCOmTacKWlloPO5V8fDEzqGRUe9VnFfxM1pB2OyHxHbE_vi6gL2lwb2jngqzPhsyNnk2CRpHwUfhX_3SmUgg5cghwPd8XtjeI7m_73wY3FDNhiI3ZeuzlkRFyWHUqQpkD9YuK_9A0YbC_nrIQZ4jHesPTym3feXkTdZ89lHZF83QnuoEfY-xlehKi563EZQaiw_CevTQMc397Q"
    pickle.dump(access_token, open(local_file_paths.PATH_ACCESS_TOKEN, "wb"))
else:
    raise ValueError("Submission is publicly available only for SIZE=0 or SIZE=1, for other sizes please contact hello@lattica.ai.")


# Get encryption params and model metadata from BE
client = submission_utils.get_lattica_client(local_file_paths)
context, hom_seq = client.get_init_data()

# Save data to local file system
pickle.dump(context, open(local_file_paths.PATH_CONTEXT, "wb"))
pickle.dump(hom_seq, open(local_file_paths.PATH_HOM_SEQ, "wb"))
