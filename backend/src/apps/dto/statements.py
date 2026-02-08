import uuid
from pydantic import BaseModel, ConfigDict


class StatementAddRequestDTO(BaseModel):
    pass


class StatementResponseDTO(BaseModel):
    pass


class StatementAddDTO(BaseModel):
    id: uuid.UUID
    pass


class StatementPatchDTO(BaseModel):
    pass


class StatementDTO(BaseModel):
    id: uuid.UUID
    pass

    model_config = ConfigDict(from_attributes=True)
