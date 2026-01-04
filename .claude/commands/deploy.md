# /deploy - 部署相关

## 描述
生成部署配置、Docker 文件、CI/CD 流水线等。

## 使用方式
```
/deploy <类型> [参数]
```

## 部署类型

### 1. Docker 部署
```
/deploy docker [--service <服务名>]
```

生成 Dockerfile 和 docker-compose.yml

### 2. CI/CD 配置
```
/deploy ci [--platform <平台>]
```

支持平台：`github`、`gitlab`、`jenkins`

### 3. Nginx 配置
```
/deploy nginx [--domain <域名>]
```

生成 Nginx 配置文件

## Docker 配置

### 后端 Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 前端 Dockerfile
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  frontend:
    build: ./platform-vue-web
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./platform-fastapi-server
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://root:password@mysql:3306/testdb
    depends_on:
      - mysql

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=testdb
    volumes:
      - mysql-data:/var/lib/mysql

volumes:
  mysql-data:
```

## CI/CD 配置

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and push Docker image
        run: |
          docker build -t myapp:latest .
          docker push registry.example.com/myapp:latest
      
      - name: Deploy to server
        run: |
          ssh user@server "docker pull && docker-compose up -d"
```

### GitLab CI
```yaml
# .gitlab-ci.yml
stages:
  - build
  - deploy

build:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

deploy:
  stage: deploy
  script:
    - ssh user@server "docker-compose pull && docker-compose up -d"
  only:
    - main
```

## Nginx 配置

```nginx
server {
    listen 80;
    server_name example.com;
    
    # 前端
    location / {
        root /usr/share/nginx/html;
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

## 常用命令

```bash
# Docker
docker-compose up -d          # 启动
docker-compose down           # 停止
docker-compose logs -f        # 查看日志
docker-compose up -d --build  # 重新构建

# 服务器
systemctl status nginx        # Nginx 状态
systemctl reload nginx        # 重载配置
```

## 输出位置
- Dockerfile：项目根目录
- docker-compose.yml：项目根目录
- nginx.conf：`deploy/nginx.conf`
- CI 配置：`.github/workflows/` 或 `.gitlab-ci.yml`

## 注意事项
- 敏感信息使用环境变量
- 生产环境使用固定版本标签
- 配置日志轮转避免磁盘满
- 设置健康检查和资源限制
