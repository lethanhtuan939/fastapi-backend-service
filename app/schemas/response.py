from typing import Generic, TypeVar, Optional, Any, List, Dict
from pydantic import Field
from pydantic.generics import GenericModel

DataT = TypeVar("DataT")


class APIResponse(GenericModel, Generic[DataT]):
    code: int = Field(...)
    status: str = Field(...)
    message: Optional[str] = Field(None)
    data: Optional[DataT] = Field(None)
    errors: Optional[List[Dict[str, Any]]] = Field(None)
    meta: Optional[Dict[str, Any]] = Field(None)
    url: Optional[str] = Field(None)
    timestamp: Optional[str] = Field(None)

    class Config:
        from_attributes = True
        json_encoders = {}
