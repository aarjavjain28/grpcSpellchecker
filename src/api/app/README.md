# Cloud Run Template Service
## 1. Overview of App Code
The service works by using a`proto` file to generate the grpc servicer classes under the name `predictor_pb2(_grpc).py`. 
The Server class is inherited by the `PredictionService` class in, `prediction/predictor.py`. 

The `PredictionService` 
object contains 4 methods;
1. `load_model`: Loads local model binary into the class for prediction
2. `predict`: Envokes the predict method of the model with some error handling
3. `build_response`: Wrapper class for predict that places the model output into a format compatible with the schema set by the `proto` file
4. GetPredictions: The inherited method that receives the input `Request` and returns the output `Response`.

The `PredictionService` is placed into the server in the service.py main function, and the server is started.
Additionally, there is some logic to download the model from GCS and pass the binary path to the Prediction service.

## 2 How to make your changes
There are 5 things you will need to change to configure the template for your app.

1. The model config in `config.yaml`:
```yaml
model_metadata_config:
  version: YOUR MODEL VERSION
  name: YOUR MODEL NAME
model_download_config:
  blob_prefix: MODEL PREFIX IN GCS
  destination_path: local/path
```
This will download the model to the `destination_path` before the service begins running.

2. In the `predictor.proto` you need to update the `Prediction` message to match the type that your model outputs.
```protobuf
message Prediction {
    type field_name = 1;
}
```
Once this is done from the `app` directory run `make` this will regenerate the proto files, (Note: These files are 
automatically generated at deployment so you do not need them commited to your repo).

3. In the `PredictionService` object you will need to configure it for your specific model.
    
    3.i)    Update `__init__` to generate the model hash using thg-gcp-utils and add it to the hash field of the metadata.
    
    3.ii)   Update `load_model` to load your model into the predictor object.
    
    3.iii)  Update `predict` to implement your invocation of your model and any other services you require, if you call 
    any other services be sure to add the model hash of said service to the model hash in the metadata.
    
    3.iv)   Update `build_response` to construct your responses following any error handling you have implemented in 
    your `predict` method. 
     
