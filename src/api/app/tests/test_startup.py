import os
import time
from subprocess import Popen

import grpc
import pytest
import predictor_pb2 as pb2
import predictor_pb2_grpc as pb2_grpc


@pytest.fixture
def start_local_server() -> None:
    p = Popen(["python", "service.py", "--port", "8070"])
    time.sleep(7)
    yield
    time.sleep(1)
    p.terminate()


def test_model_download(start_local_server) -> None:
    assert os.path.isdir("cloud-run-template")


def test_valid_request(start_local_server) -> None:
    channel = grpc.insecure_channel('localhost:8070')
    client = pb2_grpc.LargeModelPredictorStub(channel)

    request = pb2.Request(input="A test Message")
    response = client.get_predictions(request)

    assert response.status == "OK"
    assert response.data.value == "A test Message"


def test_invalid_request(start_local_server) -> None:
    channel = grpc.insecure_channel('localhost:8070')
    client = pb2_grpc.LargeModelPredictorStub(channel)

    request = pb2.Request(input="123456789012345678901234567890")
    response = client.get_predictions(request)

    assert response.status == "ERROR"
    assert response.message == "There was an error: Request too big!"
