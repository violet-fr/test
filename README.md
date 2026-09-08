# 智慧园区综合管理平台

## 环境要求

- **后端**：Python 3.11+、PostgreSQL 16（带 pgvector）、Redis 7
- **前端**：Node.js 18+、npm 9+
- **AI 服务**：Python 3.11+、Ollama（可选，本地大模型）
- **部署**：Docker 24+、Docker Compose 2+

## 目录结构

```
backend/        # 业务后端（FastAPI + SQLAlchemy 2.0）
ai-service/     # AI 服务（RAG / 人脸 / 图像识别）
web-admin/      # 管理后台（Vue3 + Element Plus）
web-screen/     # 数据大屏（Vue3 + ECharts）
miniapp/        # 微信小程序（uni-app）
deploy/         # Docker Compose + Nginx + 初始化脚本
docs/           # 技术方案、API 接口定义、开发任务清单
```

## 快速启动（Docker Compose）

```bash
cd deploy

# 1. 配置环境变量（填入实际密码）
cp .env.example .env
cp ../backend/.env.example ../backend/.env

# 2. 启动全栈
docker-compose up -d

# 3. 执行数据库迁移 + 初始化数据
docker-compose exec backend alembic upgrade head
docker-compose exec -e ADMIN_PASSWORD=<你的密码> backend python /deploy/init_data.py
```

- 后端 API 文档：http://localhost:8000/docs
- 管理后台：http://localhost
- 默认账号：`admin` / 你在 `ADMIN_PASSWORD` 中设置的密码

## 本地开发启动

### 后端

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # 填入 DATABASE_URL / SECRET_KEY
alembic upgrade head
python ../deploy/init_data.py # 初始化 admin 账号
uvicorn app.main:app --reload
```

### AI 服务

```bash
cd ai-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### 管理后台

```bash
cd web-admin
npm install
npm run dev        # http://localhost:5173
```

## 打包构建

```bash
# 管理后台
cd web-admin && npm run build    # 产物：dist/

# 后端 / AI 服务
docker build -t park-backend ./backend
docker build -t park-ai-service ./ai-service
```

## 代码质量

```bash
# 后端（Ruff）
cd backend && pip install -r requirements-dev.txt
ruff check . && ruff format .

# 前端（ESLint + Prettier）
cd web-admin
npm run lint
npm run format
```

## 接口文档

- [API 接口定义](docs/API接口定义.md)
- [开发任务清单](docs/开发任务清单.md)
- [技术方案](.trae/documents/智慧园区综合管理平台技术方案.md)

## 安全说明

- 所有密钥、密码通过环境变量注入，**禁止硬编码**
- `.env` 已加入 `.gitignore`，不会提交版本库
- 人脸原图提取特征后立即删除，仅存储特征向量
