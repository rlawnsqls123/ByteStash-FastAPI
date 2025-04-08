from pydantic import BaseModel
from typing import Optional

class Code(BaseModel):
    id: int
    title: str
    tag: Optional[str]
