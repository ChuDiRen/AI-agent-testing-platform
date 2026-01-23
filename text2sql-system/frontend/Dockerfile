# Text2SQL智能查询系统 - 前端

FROM node:18-alpine

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制应用代码
COPY src ./src
COPY public ./public

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["npm", "start"]
