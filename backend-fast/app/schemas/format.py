from pydantic import BaseModel
from typing import Optional


class FormatResponse(BaseModel):
    id: str
    name: str
    type: str
    platformId: Optional[str] = None
    category: Optional[str] = None
    width: int
    height: int

    class Config:
        from_attributes = True
