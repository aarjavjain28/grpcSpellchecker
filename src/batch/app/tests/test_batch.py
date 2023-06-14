import json
import os
import shutil
from subprocess import Popen, PIPE
import pytest
from thg_gcp_utils.storage import download_directory_to_local, get_bucket_name, \
    BucketSuffix
from google.cloud import storage

input_file = "mlops-template/test/inputs/test_input.jsonl"
output_file = "mlops-template/test/outputs/test_output.jsonl"


@pytest.fixture
def remove_local_files() -> None:
    yield
    shutil.rmtree("mlops-template/")
    os.remove("test_output.jsonl") if os.path.exists("test_output.jsonl") else None


@pytest.fixture
def remove_gcs_files() -> None:
    yield
    client = storage.Client()
    bucket = client.get_bucket(get_bucket_name(BucketSuffix.BATCH_BUCKET))
    blob = bucket.blob(output_file)
    blob.delete()


def test_end_to_end(remove_local_files: pytest.fixture,
                    remove_gcs_files: pytest.fixture) -> None:
    p = Popen(["python", "main.py", input_file, output_file], stdout=PIPE,
              stderr=PIPE)

    p.wait()

    download_directory_to_local(
        bucket_name=get_bucket_name(BucketSuffix.BATCH_BUCKET), blob_prefix=output_file
    )

    with open(output_file) as f:
        data = [json.loads(line) for line in f]
        assert data == [{"id": 1, "content": "example 1", "upperCase": "EXAMPLE 1"},
                        {"id": 2, "content": "example 2", "upperCase": "EXAMPLE 2"},
                        {"id": 3, "content": "example 3", "upperCase": "EXAMPLE 3"}]
