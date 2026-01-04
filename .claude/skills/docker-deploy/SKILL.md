# Docker 部署技能

## 触发条件
当用户提到：Docker、容器、部署、Dockerfile、docker-compose、K8s

## Dockerfile 模板

### Python FastAPI
```dockerfile
# platform-fastapi-server/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Vue 前端
```dockerfile
# platform-vue-web/Dockerfile
# 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install --registry=https://registry.npmmirror.com
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx 配置
```nginx
# platform-vue-web/nginx.conf
server {
    listen 80;
    server_name localhost;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

## Docker Compose

### 完整配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  # 前端
  frontend:
    build: ./platform-vue-web
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - app-network

  # 后端
  backend:
    build: ./platform-fastapi-server
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://root:password@mysql:3306/testdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - mysql
      - redis
    volumes:
      - ./logs:/app/logs
    networks:
      - app-network

  # MySQL
  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=testdb
    volumes:
      - mysql-data:/var/lib/mysql
      - ./database-setup:/docker-entrypoint-initdb.d
    networks:
      - app-network

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - app-network

  # MinIO
  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=admin
      - MINIO_ROOT_PASSWORD=admin123
    volumes:
      - minio-data:/data
    command: server /data --console-address ":9001"
    networks:
      - app-network

volumes:
  mysql-data:
  redis-data:
  minio-data:

networks:
  app-network:
    driver: bridge
```

### 开发环境配置
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  backend:
    build:
      context: ./platform-fastapi-server
      dockerfile: Dockerfile.dev
    volumes:
      - ./platform-fastapi-server:/app  # 热重载
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 常用命令

### 构建和运行
```bash
# 构建镜像
docker build -t myapp:latest .

# 运行容器
docker run -d -p 8000:8000 --name myapp myapp:latest

# 使用 compose
docker-compose up -d          # 启动
docker-compose down           # 停止
docker-compose up -d --build  # 重新构建并启动
docker-compose logs -f        # 查看日志
```

### 容器管理
```bash
# 查看容器
docker ps                     # 运行中
docker ps -a                  # 全部

# 进入容器
docker exec -it container_name bash

# 查看日志
docker logs -f container_name

# 停止/删除
docker stop container_name
docker rm container_name

# 清理
docker system prune -a        # 清理未使用资源
```

### 镜像管理
```bash
# 查看镜像
docker images

# 删除镜像
docker rmi image_name

# 导出/导入
docker save -o myapp.tar myapp:latest
docker load -i myapp.tar

# 推送到仓库
docker tag myapp:latest registry.example.com/myapp:latest
docker push registry.example.com/myapp:latest
```

## 生产环境优化

### 多阶段构建
```dockerfile
# 减小镜像体积
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 健康检查
```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### 资源限制
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 日志配置
```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 环境变量管理

```bash
# .env 文件
DATABASE_URL=mysql+pymysql://root:password@mysql:3306/testdb
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key

# docker-compose.yml
services:
  backend:
    env_file:
      - .env
```

## 注意事项
1. 不要在镜像中存储敏感信息
2. 使用 .dockerignore 排除不需要的文件
3. 生产环境使用固定版本标签
4. 定期更新基础镜像
5. 配置日志轮转，避免磁盘占满
