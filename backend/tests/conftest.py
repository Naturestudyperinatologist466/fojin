import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import ASGITransport, AsyncClient


def _make_mock_es(search_return=None):
    """Create a mock ES client with configurable search return value."""
    mock = AsyncMock()
    if search_return is None:
        search_return = {
            "hits": {
                "total": {"value": 0},
                "hits": [],
            },
        }
    mock.search.return_value = search_return
    return mock


@pytest.fixture
def mock_es():
    return _make_mock_es({
        "hits": {
            "total": {"value": 2},
            "hits": [
                {
                    "_id": "1",
                    "_score": 5.0,
                    "_source": {
                        "id": 1,
                        "cbeta_id": "T0001",
                        "title_zh": "长阿含经",
                        "source_code": "cbeta",
                    },
                    "highlight": {},
                },
                {
                    "_id": "2",
                    "_score": 3.0,
                    "_source": {
                        "id": 2,
                        "cbeta_id": "T0002",
                        "title_zh": "般若波罗蜜多心经",
                        "source_code": "cbeta",
                    },
                    "highlight": {},
                },
            ],
        },
    })


@pytest.fixture
async def client(mock_es):
    """Async HTTP client with mocked ES (patched at each consumer module)."""
    # Patch get_es at every module that imports it, so the already-bound symbols
    # point to our mock instead of the real ES client.
    with patch("app.api.search.get_es", return_value=mock_es), \
         patch("app.core.elasticsearch.init_es", new_callable=AsyncMock), \
         patch("app.core.elasticsearch.close_es", new_callable=AsyncMock), \
         patch("app.main.aioredis") as mock_redis_mod:
        mock_redis = AsyncMock()
        mock_redis_mod.from_url.return_value = mock_redis

        from app.main import app
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
