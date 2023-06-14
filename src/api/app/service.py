import argparse
import asyncio
import logging
import os
from concurrent import futures

import grpc
from grpc._server import _Server
from prediction.predictor import PredictionService
import predictor_pb2_grpc as pb2_grpc

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)


async def main(FLAGS):
    server: _Server = grpc.server(futures.ThreadPoolExecutor(max_workers=1000))
    pb2_grpc.add_LargeModelPredictorServicer_to_server(
        servicer=PredictionService(),
        server=server
    )

    server.add_insecure_port(f"[::]:{FLAGS.port}")
    server.start()
    logging.info(f"Server started on port {FLAGS.port}")
    server.wait_for_termination()


if __name__ == '__main__':
    PORT = os.environ.get('PORT', 8081)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        default=int(PORT),
        type=int,
        help="Port number for gRPC server"
    )

    FLAGS, unparsed = parser.parse_known_args()
    if unparsed:
        logging.warning("Unparsed arguments: {}".format(unparsed))

    logging.info("Arguments: {}".format(FLAGS))
    asyncio.run(main(FLAGS))
