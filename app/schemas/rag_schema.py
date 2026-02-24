from pydantic import BaseModel

class RAGRequest(BaseModel):
    query: str

class RAGResponse(BaseModel):
    answer: str
    status: str = "success"
