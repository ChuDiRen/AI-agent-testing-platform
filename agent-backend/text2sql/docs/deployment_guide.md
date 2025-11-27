# LangGraph 部署指南

本文档说明如何部署Text2SQL系统。

## 部署方式

### 1. LangGraph 开发模式

适用于本地开发和调试：

```bash
cd agent-backend
langgraph dev --port 2024
```

特性：
- 热重载
- 集成LangGraph Studio
- 详细日志

### 2. LangGraph 生产模式

```bash
langgraph up --port 8123
```

### 3. 自定义FastAPI服务

```bash
python -m text2sql.api.server
```

或使用uvicorn：

```bash
uvicorn text2sql.api.server:app --host 0.0.0.0 --port 8000
```

## 配置

### langgraph.json

```json
{
  "$schema": "https://langgra.ph/schema.json",
  "dependencies": ["."],
  "graphs": {
    "text2sql_agent": "./text2sql/chat_graph.py:get_app",
    "text2sql_stream": "./text2sql/chat_graph.py:get_stream_app"
  },
  "env": ".env",
  "python_version": "3.11"
}
```

### 环境变量 (.env)

```bash
# LLM配置
SILICONFLOW_API_KEY=your_api_key

# 数据库
DATABASE_URL=mysql://user:pass@localhost/db

# 服务配置
PORT=8000
DEBUG=false

# 限流
RATE_LIMIT_PER_MINUTE=60
MAX_CONCURRENT_REQUESTS=100
```

## Docker部署

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-m", "text2sql.api.server"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  text2sql:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SILICONFLOW_API_KEY=${SILICONFLOW_API_KEY}
    volumes:
      - ./data:/app/data

  langgraph:
    image: langchain/langgraph-api:latest
    ports:
      - "2024:2024"
    environment:
      - SILICONFLOW_API_KEY=${SILICONFLOW_API_KEY}
    volumes:
      - .:/app
    command: langgraph dev --port 2024
```

## API调用

### LangGraph SDK (Python)

```python
from langgraph_sdk import get_sync_client

client = get_sync_client(url="http://localhost:2024")

for chunk in client.runs.stream(
    None,
    "text2sql_agent",
    input={"messages": [{"role": "human", "content": "查询所有用户"}]},
    stream_mode="messages-tuple"
):
    print(chunk.data)
```

### REST API

```bash
# 查询
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "查询用户", "connection_id": 0}'

# 流式查询
curl -X POST http://localhost:8000/api/v1/query/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "查询用户"}'

# LangGraph流式
curl -s --request POST \
  --url "http://localhost:2024/runs/stream" \
  --header 'Content-Type: application/json' \
  --data '{
    "assistant_id": "text2sql_agent",
    "input": {"messages": [{"role": "human", "content": "查询用户"}]},
    "stream_mode": "messages-tuple"
  }'
```

## 监控

### 健康检查

```bash
# FastAPI
curl http://localhost:8000/ok

# LangGraph
curl http://localhost:2024/ok
```

### 日志

日志输出到标准输出，可使用日志收集工具：

```bash
# Docker日志
docker logs -f text2sql

# 重定向到文件
python -m text2sql.api.server 2>&1 | tee app.log
```

## 扩展

### 水平扩展

使用负载均衡器部署多个实例：

```nginx
upstream text2sql {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://text2sql;
    }
}
```

### 数据库连接池

调整配置以支持高并发：

```python
from text2sql.config import DatabaseConfig

config = DatabaseConfig(
    pool_size=50,
    max_overflow=20,
    pool_timeout=30
)
```

## 故障排除

### 常见问题

1. **API Key无效**
   - 检查环境变量是否正确设置
   - 确认API Key未过期

2. **连接超时**
   - 检查网络连接
   - 增加超时配置

3. **内存不足**
   - 减少并发数
   - 增加服务器内存

### 调试模式

```bash
DEBUG=true python -m text2sql.api.server
```
