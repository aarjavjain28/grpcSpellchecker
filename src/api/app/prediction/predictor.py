import logging
import os
from datetime import datetime
from typing import Optional, Any

import predictor_pb2 as pb2
import predictor_pb2_grpc as pb2_grpc
from model_types.model_types import ModelPrediction, ModelInput, Prediction
from thg_gcp_utils.config import get_config
from thg_gcp_utils.storage import download_directory_to_local, get_bucket_name, BucketSuffix

from spellchecker import SpellcheckerAPI

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO
)

# Loading configuration information from config.yaml
file_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join("config.yaml")
config = get_config(CONFIG_PATH)


class PredictionService(pb2_grpc.LargeModelPredictorServicer):
    """
    A class to act as the Prediction service for the cloud run app
    """

    def __init__(self):
        """
        Initialistion with the model path passed in to generate model.
        :param model_path: Path to local model binary
        """
        logging.info(f"Initialising Predictor")
        service_ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.model_meta_config = config['model_metadata_config']
        self.model_download_config = config['model_download_config']
        self.model_metadata = pb2.Metadata(modelVersion=self.model_meta_config['version'],
                                           modelName=self.model_meta_config['name'],
                                           serviceCreationTimestamp=service_ts)
        self.model, model_hash = self.load_model()
        self.model_metadata.modelHash = model_hash
        self.spellchecker = SpellcheckerAPI(config)

    def load_model(self) -> Any:
        """
        Load model Binary from model path
        :param model_path: path to local model binary
        :return: Returns compiled model
        """
        model_list = download_directory_to_local(bucket_name=get_bucket_name(BucketSuffix.MODEL_BUCKET),
                                                 blob_prefix=self.model_download_config["blob_prefix"])

        model_path = os.path.join(self.model_download_config["destination_path"],
                                  self.model_download_config["blob_prefix"],
                                  model_list[0])

        model_hash = "Hash gathered by downloading the model"

        # FIXME: Load your model from path/to/binary here
        model = model_path

        return model, model_hash

    def predict(self, model_input: ModelInput) -> Optional[Prediction]:#-> Optional[ModelPrediction]:
        """
        Predict method of model invoked.
        :param model_input: Input to model
        :return: Model Output
        """
        # FIXME: Your model.predict method goes here


        # Some check on the request to determine success of prediction.
        # if len(model_input.input) > 20:
        #     raise Exception("Request too big!")

        predictions = self.spellchecker.predict(model_input.input)[0]

        return predictions
        #return ModelPrediction(prediction=model_input.input)

    def get_predictions(self, request: pb2.Request, context) -> pb2.Response:
        """
        GetPredictions Method inherited from LargeModelPredictorServicer.
        :param request: Request sent to service
        :param context: not used in this case
        :return: Response from server
        """
        logging.info("Predicting now ........")
        try:
            model_prediction = self.predict(ModelInput(input=request.input))
            predictions = pb2.Prediction(total_words=model_prediction.total_words ,well_spelt_words= model_prediction.well_spelt_words, ratio=model_prediction.ratio, suggestions=model_prediction.suggestions,supported_language=model_prediction.supported_language )
            response = pb2.Response(status="OK", message="All Good", metadata=[self.model_metadata],
                                    data=predictions)
        except Exception as e:
            response = pb2.Response(status="ERROR", message=f"There was an error: {e}", metadata=[self.model_metadata],
                                    data=pb2.Prediction())
        return response
