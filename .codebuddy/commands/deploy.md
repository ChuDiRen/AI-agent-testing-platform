---
description: 项目部署命令
---

# 命令：deploy

## 功能描述

将前后端项目部署到云平台，支持多种部署方式（Docker、云函数、静态托管等）。

## 使用方式

```
/deploy
```

或

```
/deploy <目标环境>
```

## 参数说明

### 部署环境
- `--env=production` - 生产环境
- `--env=staging` - 预发布环境
- `--env=development` - 开发环境

### 部署方式
- `--method=docker` - Docker容器部署
- `--method=cloud-function` - 云函数部署
- `--method=static` - 静态托管（前端）
- `--method=serverless` - Serverless部署

### 目标平台
- `--platform=tcb` - 腾讯云云开发
- `--platform=cloud-studio` - Cloud Studio
- `--platform=lighthouse` - 腾讯云轻量服务器
- `--platform=anydev` - AnyDev 云研发

### 其他选项
- `--frontend-only` - 仅部署前端
- `--backend-only` - 仅部署后端
- `--with-migration` - 执行数据库迁移
- `--with-tests` - 部署前运行测试

## 执行流程

1. **环境检查**：
   - 检查代码完整性
   - 检查配置文件
   - 检查依赖项

2. **构建打包**：
   - 前端构建：`pnpm build`
   - 后端构建：`mvn package` 或 `poetry build`
   - 生成Docker镜像（如需要）

3. **测试验证**：
   - 运行自动化测试
   - 健康检查
   - 性能测试（可选）

4. **部署执行**：
   - 上传代码/镜像
   - 配置环境变量
   - 启动服务
   - 配置域名/CDN

5. **部署验证**：
   - 访问测试
   - 功能验证
   - 监控检查

6. **文档生成**：
   - 生成部署报告
   - 记录部署日志

## Docker部署方式

### Dockerfile生成

**前端Dockerfile**：
```dockerfile
# 前端/Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**后端Dockerfile（Java）**：
```dockerfile
# 后端/Dockerfile
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**后端Dockerfile（Python）**：
```dockerfile
# 后端/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry config virtualenvs.create false
RUN poetry install --no-dev
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose配置

```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## 腾讯云部署方式

### 云开发（TCB）部署

```bash
# 前端部署
tcb hosting deploy ./frontend/dist -e prod

# 云函数部署
tcb functions deploy ./backend -e prod
```

### Cloud Studio部署

```bash
# 连接Cloud Studio
# 自动识别项目类型并配置
# 一键部署到云服务器
```

## 输出格式

```markdown
【部署执行中...】

==================== 环境检查 ====================

✅ 代码完整性检查通过
✅ 配置文件检查通过
✅ 依赖项检查通过

==================== 构建打包 ====================

✅ 前端构建完成 (耗时: 45s)
   输出：frontend/dist/
   大小：2.3MB

✅ 后端构建完成 (耗时: 120s)
   输出：backend/target/app.jar
   大小：85MB

✅ Docker镜像构建完成
   前端：project-frontend:latest
   后端：project-backend:latest

==================== 测试验证 ====================

✅ 单元测试通过 (覆盖率: 92%)
✅ API测试通过 (通过率: 95%)
✅ 健康检查通过

==================== 部署执行 ====================

✅ 上传代码包到服务器
✅ 配置环境变量
✅ 启动服务
✅ 配置域名和SSL

==================== 部署完成 ====================

## 访问地址

前端：https://app.example.com
后端API：https://api.example.com
数据库：db.example.com:5432

## 部署信息

- 部署环境：Production
- 部署时间：2025-01-16 10:30:00
- 部署版本：v1.0.0
- 部署方式：Docker

## 监控地址

- 应用监控：https://monitor.example.com
- 日志查看：https://logs.example.com

## 下一步

1. 访问应用进行功能验证
2. 配置告警通知
3. 备份数据库

## 回滚命令

如果需要回滚，执行：
/deploy --rollback --version=v0.9.0
```

## 相关文件

```
deploy/
├── docker-compose.yml
├── nginx.conf
├── scripts/
│   ├── build.sh
│   ├── deploy.sh
│   └── rollback.sh
└── configs/
    ├── production.env
    └── staging.env
```

## 示例

```
/deploy --env=production --method=docker --platform=tcb
```

```
/deploy --frontend-only --env=staging
```

```
/deploy --with-tests --with-migration
```

## 相关命令

- `/test-api` - API测试
- `/test-e2e` - E2E测试
- `/start-project` - 启动项目
