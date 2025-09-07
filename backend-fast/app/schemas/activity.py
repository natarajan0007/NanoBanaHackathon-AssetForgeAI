from pydantic import BaseModel
from datetime import datetime
import uuid

class Activity(BaseModel):
    id: uuid.UUID
    projectName: str
    status: str
    createdAt: datetime

    class Config:
        from_attributes = True
