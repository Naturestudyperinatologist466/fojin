from pydantic import BaseModel


class DianjinSearchHit(BaseModel):
    """搜索结果项，从典津 standardFields 提取。"""
    id: str = ""
    title: str = ""
    datasource_name: str | None = None
    datasource_category: str | None = None
    datasource_tags: list[str] = []
    collection: str | None = None
    main_responsibility: str | None = None
    edition: str | None = None
    detail_url: str | None = None
    score: float | None = None


class DianjinSearchResponse(BaseModel):
    total: int = 0
    page: int = 1
    size: int = 20
    results: list[DianjinSearchHit] = []
    search_time: float | None = None
    error: str | None = None


class FederatedSearchResponse(BaseModel):
    local_total: int = 0
    local_results: list[dict] = []
    dianjin_total: int = 0
    dianjin_results: list[DianjinSearchHit] = []
    dianjin_error: str | None = None
    combined_total: int = 0


class DianjinHealthResponse(BaseModel):
    configured: bool = False
    public_api: bool = False
    search_api: bool = False
    datasource_count: int = 0
    error: str | None = None


class DianjinDatasource(BaseModel):
    """典津数据源，匹配 /api/public/datasources 实际响应。"""
    id: str = ""
    name: str = ""
    code: str = ""
    description: str = ""
    category: str = ""
    tags: list[str] = []
    institution_code: str = ""
    record_count: int = 0


class DianjinDatasourcePage(BaseModel):
    """分页响应。"""
    items: list[DianjinDatasource] = []
    total: int = 0
    page: int = 1
    size: int = 20
    total_pages: int = 0
