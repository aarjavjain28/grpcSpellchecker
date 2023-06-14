from pydantic import BaseModel


class ModelInput(BaseModel):
    input: str


class ModelPrediction(BaseModel):
    prediction: str

