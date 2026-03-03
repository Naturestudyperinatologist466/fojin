from datetime import datetime

from pydantic import BaseModel


class IIIFManifestResponse(BaseModel):
    id: int
    text_id: int
    source_id: int
    label: str
    manifest_url: str
    thumbnail_url: str | None = None
    provider: str
    rights: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
