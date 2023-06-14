import os
import sys
from thg_gcp_utils.config import get_config
from thg_gcp_utils.storage import (
    download_directory_to_local,
    upload_files, get_bucket_name, BucketSuffix, load_jsonlines_file_from_gcs,
    append_data_to_local_file
)
from typing import List
from model_types import InputData, Predictions

if __name__ == "__main__":
    # The file to be processed. A GCS file path (excluding bucket name)
    input_file = sys.argv[1]
    # File path on GCS, where to store the prediction, excludes bucket name.
    output_file = sys.argv[2]

    # The name of the file, used for storing model predictions
    local_output_file = output_file.split(os.sep)[-1]

    # Loading configuration information from config.yaml
    file_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(file_dir, "config.yaml")
    config = get_config(config_path)

    batch_processing_size = config["batch_processing_size"]
    model_bucket_name = get_bucket_name(bucket_suffix=BucketSuffix.MODEL_BUCKET)
    model_blob_prefix = config["model_blob_prefix"]

    download_directory_to_local(
        bucket_name=model_bucket_name, blob_prefix=model_blob_prefix
    )

    # Read the data in input_file in chunks of batch_processing_size, performing
    # predictions on each chunk and appending
    # to the local_output_file
    for data in load_jsonlines_file_from_gcs(
            blob_path=input_file, batch_processing_size=batch_processing_size
    ):
        # performing pydantic validation on input data
        for entry in data:
            InputData(**entry)

        predictions = [{**entry, "upperCase": entry[
            "content"].upper()} for entry in data]
        append_data_to_local_file(
            data=predictions, local_output_file=local_output_file
        )

        # performing pydantic validation on predictions
        for entry in predictions:
            Predictions(**entry)

    # When all data has been processed, upload the local_output_file to output_file
    # GCS path
    upload_files(
        bucket_name=get_bucket_name(bucket_suffix=BucketSuffix.BATCH_BUCKET),
        destination_blob_prefix=os.sep.join(output_file.split(os.sep)[:-1]),
        source_blob_prefix=".",
        file_list=[local_output_file],
        exist_ok=True,
    )
