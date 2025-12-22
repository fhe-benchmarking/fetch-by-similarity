import os

from lattica_query.lattica_query_client import QueryClient

from constants import TOKEN


def get_query_client():
    if os.getenv('LATTICA_RUN_MODE') == 'LOCAL':
        from lattica_query.dev_utils.lattica_query_client_local import \
            LocalQueryClient
        client = LocalQueryClient(TOKEN)
    else:
        client = QueryClient(TOKEN)
    return client
