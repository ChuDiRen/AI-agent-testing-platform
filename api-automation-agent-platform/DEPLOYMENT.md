# 接口自动化智能体平台 - 部署指南

本文档提供完整的部署指南，涵盖开发环境、生产环境和 Docker 部署。

## 📋 目录

- [系统要求](#系统要求)
- [环境配置](#环境配置)
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [Docker 部署](#docker-部署)
- [验证部署](#验证部署)
- [故障排除](#故障排除)

---

## 系统要求

### 最低要求

| 组件 | 要求 |
|--------|--------|
| 操作系统 | Linux, macOS, Windows 10+ |
| Python | 3.11+ |
| 内存 | 4GB RAM (推荐 8GB+) |
| 磁盘 | 10GB 可用空间 |

### Python 依赖

```bash
# 核心框架
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
sqlmodel>=0.0.14
python-multipart>=0.0.6

# LLM 服务
openai>=1.10.0  # OpenAI GPT
anthropic>=0.18.0  # Anthropic Claude

# RAG 引擎
chromadb>=0.4.22
sentence-transformers>=2.3.1

# 测试框架
playwright>=1.40.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-playwright>=0.4.0

# 工具库
httpx>=0.26.0
pyyaml>=6.0.1
jsonschema>=4.21.0
python-dotenv>=1.0.0
aiofiles>=23.2.1
python-json-logger>=2.0.7
```

### 可选依赖（增强功能）

```bash
# PDF 解析
PyPDF2>=3.0.0

# 性能监控
prometheus-client>=0.19.0

# 数据库（PostgreSQL，替代 SQLite）
psycopg2-binary>=2.9.9
```

---

## 环境配置

### 1. 创建环境文件

复制并编辑 `.env.example`：

```bash
cp .env.example .env
```

### 2. 配置必需的环境变量

```bash
# ==================== 应用配置 ====================
APP_NAME=API Automation Agent Platform
APP_VERSION=0.2.0
DEBUG=false
HOST=0.0.0.0
PORT=8000

# ==================== 数据库配置 ====================
DATABASE_URL=sqlite:///./data/app.db
# 或使用 PostgreSQL:
# DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/api_platform

# ==================== LLM 配置 ====================
LLM_PROVIDER=openai  # openai | anthropic
LLM_MODEL=gpt-4-turbo-preview  # 或 claude-3-opus-20240229
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4000
LLM_TIMEOUT=60

# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here
# 从 https://platform.openai.com/api-keys 获取

# Anthropic API Key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
# 从 https://console.anthropic.com/settings/keys 获取

# ==================== RAG 配置 ====================
RAG_PERSIST_DIR=./data/chromadb
RAG_COLLECTION_NAME=api_knowledge
RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=50

# ==================== 测试执行配置 ====================
TEST_BASE_URL=http://localhost:8000
TEST_TIMEOUT=60000
TEST_PARALLEL_ENABLED=true
TEST_MAX_CONCURRENT=10

# ==================== 日志配置 ====================
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR | CRITICAL
LOG_FILE=logs/app.log
LOG_JSON_OUTPUT=false

# ==================== CORS 配置 ====================
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# ==================== 安全配置 ====================
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET=your-jwt-secret-change-in-production
SESSION_EXPIRE_HOURS=24
```

---

## 开发环境部署

### 步骤 1: 克隆并设置项目

```bash
# 克隆仓库
git clone <repository-url>
cd api-automation-agent-platform

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
npx playwright install

# 创建数据目录
mkdir -p data logs test_outputs
```

### 步骤 2: 配置环境

```bash
# 编辑 .env 文件
nano .env  # 或使用你喜欢的编辑器

# 至少配置：
# - LLM API keys
# - 数据库 URL
```

### 步骤 3: 初始化数据库

```bash
# 初始化数据库
python -c "from api_agent.db import init_db; init_db()"

# 验证数据库创建
ls -lh data/app.db  # 应该看到数据库文件
```

### 步骤 4: 启动 MCP 服务器（开发模式）

在单独终端窗口中启动 MCP 服务器：

```bash
# RAG Server
python -m mcp_servers.rag_server

# Automation Quality Server
python -m mcp_servers.automation_quality

# Chart Server
python -m mcp_servers.chart_server
```

### 步骤 5: 启动主应用

```bash
# 启动 FastAPI 应用
python -m api_agent.main

# 或使用 uvicorn（更多控制）
uvicorn api_agent.main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤 6: 验证部署

```bash
# 检查健康端点
curl http://localhost:8000/health

# 应该返回：
# {
#   "status": "healthy",
#   "app_name": "API Automation Agent Platform",
#   "version": "0.2.0"
# }

# 访问 API 文档
# http://localhost:8000/docs
```

---

## 生产环境部署

### 步骤 1: 系统准备

```bash
# 更新系统包
sudo apt-get update && sudo apt-get upgrade -y  # Ubuntu/Debian
# 或
# sudo yum update -y  # CentOS/RHEL

# 安装系统依赖
sudo apt-get install -y python3.11 python3.11-venv nodejs npm
```

### 步骤 2: 创建专用用户

```bash
# 创建应用用户
sudo useradd -m -s /bin/bash api-platform

# 创建应用目录
sudo mkdir -p /opt/api-platform
sudo chown api-platform:api-platform /opt/api-platform
sudo chmod 755 /opt/api-platform

# 切换到应用用户
sudo su - api-platform
cd /opt/api-platform
```

### 步骤 3: 部署应用

```bash
# 克隆代码
git clone <repository-url> app.git
cd app.git
git checkout production

# 安装依赖
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 安装 Playwright（需要 sudo）
sudo npx playwright install --with-deps

# 配置生产环境变量
sudo cp .env.example /opt/api-platform/.env
sudo nano /opt/api-platform/.env

# 初始化数据库
python -c "from api_agent.db import init_db; init_db()"

# 创建必要目录
mkdir -p /opt/api-platform/data/logs
mkdir -p /opt/api-platform/test_outputs
```

### 步骤 4: 配置 Systemd 服务

创建服务文件 `/etc/systemd/system/api-platform.service`：

```ini
[Unit]
Description=API Automation Agent Platform
After=network.target

[Service]
Type=simple
User=api-platform
WorkingDirectory=/opt/api-platform/app.git
Environment="PATH=/opt/api-platform/app.git/venv/bin"
ExecStart=/opt/api-platform/app.git/venv/bin/uvicorn api_agent.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重载 systemd 配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start api-platform

# 启用开机自启
sudo systemctl enable api-platform

# 检查状态
sudo systemctl status api-platform
```

### 步骤 5: 配置 Nginx 反向代理

创建 Nginx 配置 `/etc/nginx/sites-available/api-platform`：

```nginx
upstream api_platform {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # 日志
    access_log /var/log/nginx/api-platform-access.log;
    error_log /var/log/nginx/api-platform-error.log;

    # 反向代理
    location / {
        proxy_pass http://api_platform;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;

        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 静态文件（可选）
    location /static {
        alias /opt/api-platform/app.git/static;
        expires 30d;
    }
}
```

启用配置：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/api-platform /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

---

## Docker 部署

### Dockerfile

创建 `Dockerfile`：

```dockerfile
# 多阶段构建
FROM python:3.11-slim as builder

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    nodejs \
    npm

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright
RUN npx playwright install --with-deps chromium

# 运行时阶段
FROM python:3.11-slim

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libx11-6 \
    libxext6 \
    libxi6 \
    libxrender1 \
    x11-utils

# 复制构建产物
COPY --from=builder /app/venv /app/venv
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# 设置工作目录
WORKDIR /app

# 创建必要目录
RUN mkdir -p /app/data /app/logs /app/test_outputs

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "api_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  # 主应用
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: api-platform
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+psycopg2://postgres:password@db:5432/api_platform
      - LLM_PROVIDER=openai
      - LLM_MODEL=gpt-4-turbo-preview
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - RAG_PERSIST_DIR=/app/data/chromadb
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./test_outputs:/app/test_outputs
    depends_on:
      - db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # PostgreSQL 数据库
  db:
    image: postgres:15-alpine
    container_name: api-platform-db
    environment:
      - POSTGRES_DB=api_platform
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=change-this-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  # Redis（可选，用于缓存）
  redis:
    image: redis:7-alpine
    container_name: api-platform-redis
    ports:
      - "6379:6379"
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  default:
    name: api-platform-network
```

### 构建和启动

```bash
# 构建镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f app

# 停止服务
docker-compose down

# 停止并删除卷
docker-compose down -v
```

---

## 验证部署

### 1. 健康检查

```bash
# API 健康检查
curl http://localhost:8000/health

# 预期响应：
# {
#   "status": "healthy",
#   "app_name": "API Automation Agent Platform",
#   "version": "0.2.0"
# }
```

### 2. API 端点测试

```bash
# 测试文档上传
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Content-Type: multipart/form-data" \
  -F "file=@swagger.yaml" \
  -F "type=openapi"

# 测试任务创建
curl -X POST http://localhost:8000/api/v1/tasks/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Task", "description": "End-to-end test"}'

# 获取任务状态（使用返回的 task_id）
curl http://localhost:8000/api/v1/tasks/{task_id}
```

### 3. MCP 服务测试

```bash
# 测试 RAG 服务
echo '{"query": "test", "mode": "mix"}' | \
  python -c "import sys, json; import asyncio; exec('''
    from core.mcp_client import create_mcp_client
    async def test():
        client = await create_mcp_client()
        result = await client.call_tool('rag-server', 'rag_query_data', json.loads(sys.stdin.read()))
        print(result)
    asyncio.run(test())
    ''')"

# 测试 Chart 服务
echo '{"chartType": "pie", "data": [{"status": "passed", "count": 5}]}' | \
  python -c "import sys, json; import asyncio; exec('''
    from core.mcp_client import create_mcp_client
    async def test():
        client = await create_mcp_client()
        result = await client.call_tool('chart-server', 'chart_generate', json.loads(sys.stdin.read()))
        print(result)
    asyncio.run(test())
    ''')"
```

### 4. 端到端测试

```bash
# 运行集成测试
cd tests/integration
pytest test_e2e_integration.py -v

# 运行所有测试
pytest tests/ -v --cov=api_agent
```

---

## 故障排除

### 常见问题

#### 1. 端口被占用

**错误**：`OSError: [Errno 48] Address already in use`

**解决方案**：
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或使用不同端口
export PORT=8001
python -m api_agent.main
```

#### 2. LLM API 认证失败

**错误**：`AuthenticationError: Invalid API key`

**解决方案**：
```bash
# 验证 API key
echo $OPENAI_API_KEY

# 重新生成 API key
# OpenAI: https://platform.openai.com/api-keys
# Anthropic: https://console.anthropic.com/settings/keys

# 测试 API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### 3. MCP 服务器连接失败

**错误**：`MCPConnectionError: Failed to connect to MCP server`

**解决方案**：
```bash
# 检查 MCP 服务器是否运行
ps aux | grep mcp_servers

# 查看 MCP 服务器日志
tail -f logs/mcp-server.log

# 重启 MCP 服务器
python -m mcp_servers.rag_server
```

#### 4. 数据库锁定

**错误**：`sqlalchemy.exc.OperationalError: database is locked`

**解决方案**：
```bash
# 停止应用
pkill -f api_agent.main

# 等待几秒
sleep 3

# 重启应用
python -m api_agent.main

# 如果持续存在，删除锁文件
rm -f data/app.db-shm data/app.db-wal
```

#### 5. Playwright 浏览器未安装

**错误**：`Error: Executable doesn't exist at /root/.cache/ms-playwright`

**解决方案**：
```bash
# 手动安装 Playwright
npx playwright install --with-deps

# 或在 Docker 中，确保复制了缓存
# 检查 Dockerfile 中的 COPY 命令
```

### 日志调试

```bash
# 实时查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/app.log | grep ERROR

# 查看 MCP 服务器日志
tail -f logs/mcp-server.log

# 查看 SQL 查询（如果启用）
tail -f logs/app.log | grep "SELECT\|INSERT\|UPDATE"
```

### 性能优化

```bash
# 使用生产配置
DEBUG=false
LOG_LEVEL=WARNING

# 启用 PostgreSQL（比 SQLite 快）
DATABASE_URL=postgresql://user:pass@localhost:5432/api_platform

# 启用 Redis 缓存（如果使用）
REDIS_URL=redis://localhost:6379/0
```

---

## 监控和维护

### 1. 日志轮转

配置 logrotate `/etc/logrotate.d/api-platform`：

```
/logs/app.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 api-platform api-platform
    postrotate
        systemctl reload api-platform > /dev/null 2>&1 || true
endscript
}
```

### 2. 数据库备份

创建备份脚本 `backup_db.sh`：

```bash
#!/bin/bash
# 数据库备份脚本

BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE=$BACKUP_DIR/api_platform_$DATE.db

mkdir -p $BACKUP_DIR

# 备份数据库
cp data/app.db $DB_FILE

# 压缩备份
gzip $DB_FILE

# 删除 7 天前的备份
find $BACKUP_DIR -name "api_platform_*.db.gz" -mtime +7 -delete

echo "Backup completed: $DB_FILE.gz"
```

### 3. 监控指标

使用 Prometheus 导出指标：

```python
# 在 api_agent/api/routes.py 中添加
from prometheus_client import Counter, Histogram

# 定义指标
request_count = Counter('api_requests_total', 'Total API requests')
request_duration = Histogram('api_request_duration_seconds', 'API request duration')

# 在路由中记录
@app.get("/api/v1/tasks")
async def list_tasks():
    with request_duration.time():
        result = await task_manager.list_tasks(...)
        request_count.inc()
        return result
```

---

## 安全建议

1. **使用强密码**
   - 更改 `.env` 中的 `SECRET_KEY` 和 `JWT_SECRET`
   - 使用至少 32 字符的随机字符串

2. **启用 HTTPS**
   - 配置 SSL 证书
   - 强制所有 API 请求使用 HTTPS

3. **限制访问**
   - 配置防火墙规则
   - 使用 `CORS_ORIGINS` 白名单

4. **定期更新**
   - `pip install --upgrade -r requirements.txt`
   - 定期更新系统和依赖

5. **最小化权限**
   - 应用程序以非 root 用户运行
   - 数据库文件权限设置为 600

---

## 联系和支持

- **文档**: https://docs.yourdomain.com
- **GitHub Issues**: https://github.com/your-repo/issues
- **Email**: support@yourdomain.com

---

*部署指南版本*: 1.0.0  
*最后更新*: 2026-01-06
