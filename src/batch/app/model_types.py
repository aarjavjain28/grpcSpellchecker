from pydantic import BaseModel, StrictInt, StrictStr


class InputData(BaseModel):
    id: StrictInt
    content: StrictStr


class Predictions(BaseModel):
    id: StrictInt
    content: StrictStr
    upperCase: StrictStr
