from pydantic import BaseModel


class CitationResponse(BaseModel):
    text_id: int
    title: str
    style: str
    citation: str
