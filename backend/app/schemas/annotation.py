from datetime import datetime

from pydantic import BaseModel


class AnnotationCreate(BaseModel):
    text_id: int
    juan_num: int
    start_pos: int
    end_pos: int
    annotation_type: str  # note/correction/tag
    content: str


class AnnotationResponse(BaseModel):
    id: int
    text_id: int
    juan_num: int
    start_pos: int
    end_pos: int
    annotation_type: str
    content: str
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
