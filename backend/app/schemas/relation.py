from pydantic import BaseModel


class RelatedTextInfo(BaseModel):
    text_id: int
    cbeta_id: str
    title_zh: str
    translator: str | None = None
    dynasty: str | None = None
    lang: str = "lzh"
    relation_type: str
    confidence: float = 1.0
    note: str | None = None

    model_config = {"from_attributes": True}


class TextRelationsResponse(BaseModel):
    text_id: int
    title_zh: str
    relations: list[RelatedTextInfo]


class ParallelReadResponse(BaseModel):
    text_a: "ParallelTextContent"
    text_b: "ParallelTextContent"


class ParallelTextContent(BaseModel):
    text_id: int
    cbeta_id: str
    title_zh: str
    translator: str | None = None
    lang: str = "lzh"
    juan_num: int
    content: str
