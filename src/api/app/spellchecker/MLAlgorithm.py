from abc import abstractmethod
from typing import TypeVar, Generic, List, Optional

from pydantic.main import BaseModel

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V', bound=Optional[BaseModel])


class AsyncMLAlgorithm(Generic[T, U, V]):
    """Asynchronuous algorithm base class, used for scenarios where minimal calculations
    are performed, or I/O bound (e.g. using tensorflow serving)

    This is a generic class with three type parameters:-
    * T - the input type
    * U - the output type
    * V - global options parameters to be passed to the request (e.g. pagination)

    This has been extracted from the existing framework defined by data engineering
    with minimal modification
    """

    def __init__(self):
        pass

    @abstractmethod
    async def predict(self, input: List[T], options: Optional[V] = None) -> List[U]:
        ...

    def healthy(self) -> bool:
        return True


class MLAlgorithm(Generic[T, U, V]):
    """Synchronuous algorithm base class, used for scenarios where heavy calculations
    are performed (e.g. using pytorch/tensorflow directly).

    This is a generic class with three type parameters:-
    * T - the input type
    * U - the output type
    * V - global options parameters to be passed to the request (e.g. pagination)

    This has been extracted from the existing framework defined by data engineering
    with minimal modification
    """

    def __init__(self):
        pass

    @abstractmethod
    def predict(self, input: List[T], options: Optional[V] = None) -> List[U]:
        ...

    def healthy(self) -> bool:
        return True
