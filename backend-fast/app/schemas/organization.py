from pydantic import BaseModel
import uuid

class OrganizationSchema(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        from_attributes = True
