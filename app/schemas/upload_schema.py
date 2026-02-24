from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    status: str = "success"
    filename: str
    documents_indexed: int
