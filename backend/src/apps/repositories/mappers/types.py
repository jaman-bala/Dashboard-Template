from typing import TypeVar
from pydantic import BaseModel

from src.core.database.database import Base

TModel = TypeVar("TModel", bound=Base)
TDTO = TypeVar("TDTO", bound=BaseModel)
