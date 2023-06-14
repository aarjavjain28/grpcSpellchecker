
from typing import List, Dict
from pydantic import BaseModel


class ModelInput(BaseModel):
    input: str

class SuggestionList(BaseModel):
    suggestion: List[str]

class Prediction(BaseModel):
    total_words: str
    well_spelt_words: str
    ratio: str
    suggestions: Dict[str, SuggestionList]
    supported_language: bool

class Metadata(BaseModel):
    modelVersion: str
    modelHash: str
    modelName: str
    serviceCreationTimestamp: str

class ModelPrediction(BaseModel):
    status: str
    message: str
    metadata: List[Metadata]
    data: Prediction
