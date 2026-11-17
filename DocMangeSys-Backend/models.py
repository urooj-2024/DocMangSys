from pydantic import BaseModel
from typing import Optional

class Document(BaseModel):
    id: int
    title: str
    content: str
    file_path: Optional[str]
