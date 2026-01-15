# 多阶段构建 Dockerfile
FROM node:18-alpine AS web-builder

WORKDIR /web

# 复制前端代码
COPY web/package.json web/pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

COPY web/ ./
RUN pnpm build

# Python 后端镜像
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制后端代码
COPY app/ ./app/
COPY run.py .

# 从前端构建阶段复制构建产物
COPY --from=web-builder /web/dist ./app/static

# 创建日志目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 80

# 启动命令
CMD ["uvicorn", "app.main:application", "--host", "0.0.0.0", "--port", "80"]
