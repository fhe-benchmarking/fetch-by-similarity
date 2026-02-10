import pickle

from lattica_query.lattica_query_client import QueryClient
from harness.params import InstanceParams as HarnessInstanceParams, instance_name, PAYLOAD_DIM
import os
import io

# constants used in pre and post processing
PRECISION = 16
MARKER_VALUE = 8192
MAX_VAL = 256

def init(argv, mute_logs=True):
    if mute_logs:
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull_fd, 1)
        os.dup2(devnull_fd, 2)
        os.close(devnull_fd)

    instance_params = InstanceParams(argv)
    file_paths = LocalFilePaths(instance_params)
    return file_paths, instance_params

class InstanceParams(HarnessInstanceParams):
    def __init__(self, argv):
        self.size = int(argv[1])
        super().__init__(self.size)
        self.n_slots = 2**9 if self.size == 0 else 2**15
        self.n_cols  = self.n_slots // 64
        self.count_only = len(argv) > 2 and argv[2] == "--count_only"
        self.name = instance_name(self.size)
        self.payload_dim = PAYLOAD_DIM

class LocalFilePaths:
    def __init__(self, instance_params):
        DATA_DIR = instance_params.datadir()
        IO_DIR   = instance_params.iodir()

        self.DB_PATH      = DATA_DIR / "db.bin"
        self.PAYLOAD_PATH = DATA_DIR / "payloads.bin"
        self.QUERY_PATH   = DATA_DIR / "query.bin"


        self.PROCESSED_DB_PATH      = IO_DIR / "db.pkl"
        self.PROCESSED_PAYLOAD_PATH = IO_DIR / "payloads.pkl"
        self.PATH_CONTEXT           = IO_DIR / "context.pkl"
        self.PATH_HOM_SEQ           = IO_DIR / "hom_seq.pkl"
        self.PATH_ACCESS_TOKEN      = IO_DIR / "access_token.pkl"
        self.PATH_SK                = IO_DIR / "sk.pkl"
        self.PK_DIR                 = IO_DIR / "keys"
        self.CT_UPLOAD_DIR          = IO_DIR / "encrypted"
        self.CT_DOWNLOAD_DIR        = IO_DIR / "ciphertexts_download"
        self.PATH_RAW_RESULT        = IO_DIR / "raw_result.pkl"
        self.PREDICTIONS_PATH       = IO_DIR / "results.bin"
        self.SERVER_TIMES_PATH      = IO_DIR / "server_reported_steps.json"

        self.PK_DIR.mkdir(parents=True, exist_ok=True)
        self.CT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.CT_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

        self.PATH_EK = self.PK_DIR / "ek.pkl"

    def get_ct_upload_path(self, name):
        return self.CT_UPLOAD_DIR / f"{name}.bin"

    def get_ct_download_path(self, name):
        return self.CT_DOWNLOAD_DIR / f"{name}.bin"

def get_lattica_client(local_file_paths):
    access_token = pickle.load(open(local_file_paths.PATH_ACCESS_TOKEN, "rb"))
    return QueryClient(access_token)
