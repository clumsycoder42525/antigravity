from pydantic import BaseModel
from typing import List, Optional

class RAGRequest(BaseModel):
    query: str

class RAGResponse(BaseModel):
    answer: str
    status: str = "success"

class UploadResponse(BaseModel):
    filename: str
    chunks: int
    message: str = "File uploaded and processed successfully"
