# 佛津 (FoJin)

全球佛教古籍数字资源聚合平台 — Phase 0.5

## 快速启动

### 使用 Docker Compose

```bash
cp .env.example .env
docker compose up -d
```

服务启动后：
- 前端：http://localhost:3000
- 后端 API：http://localhost:8000/docs
- PostgreSQL：localhost:5432
- Elasticsearch：localhost:9200
- Redis：localhost:6379

### 本地开发（不使用 Docker）

**基础服务**：需要本地安装 PostgreSQL 15、Elasticsearch 8、Redis 7，或通过 Docker 仅启动基础服务：

```bash
docker compose up -d postgres elasticsearch redis
```

**后端**：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# 配置环境变量（修改 .env 中的 host 为 localhost）
alembic upgrade head
python scripts/init_es_index.py
python scripts/import_cbeta.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端**：

```bash
cd frontend
npm install
npm run dev
```

## 数据导入

```bash
cd backend
python scripts/import_cbeta.py
```

此脚本从 CBETA GitHub 仓库获取经目数据并导入 PostgreSQL + Elasticsearch。

## 技术栈

- **前端**：React 18 + TypeScript + Vite + Ant Design 5 + Zustand + TanStack Query
- **后端**：FastAPI + SQLAlchemy (async) + Pydantic
- **数据库**：PostgreSQL 15
- **搜索**：Elasticsearch 8
- **缓存**：Redis 7
- **部署**：Docker Compose
