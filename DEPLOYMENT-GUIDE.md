# Vue FastAPI Admin - 部署指南

> Copyright (c) 2025 左岚. All rights reserved.

## 📋 部署前准备

### 系统要求
- **操作系统**: Linux/macOS/Windows
- **Node.js**: >= 18.0.0
- **Python**: >= 3.8
- **数据库**: PostgreSQL/MySQL/SQLite
- **内存**: >= 2GB
- **磁盘空间**: >= 5GB

### 依赖检查
```bash
# 检查Node.js版本
node --version

# 检查Python版本
python --version

# 检查包管理器
pnpm --version
pip --version
```

## 🚀 快速部署

### 方式一：一键部署（推荐）
```bash
# 1. 克隆项目
git clone <your-repo-url>
cd vue-fastapi-admin

# 2. 一键启动
./start-full-project.sh

# 3. 测试功能
./test-complete-features.sh
```

### 方式二：分步部署
```bash
# 1. 安装前端依赖
./setup-naive-frontend.sh

# 2. 启动后端服务
cd AI-agent-backend
python main.py

# 3. 启动前端服务
cd AI-agent-frontend-naive
pnpm dev

# 4. 测试API连接
./test-api-connection.sh
```

## 🔧 环境配置

### 后端配置
编辑 `AI-agent-backend/.env` 文件：
```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# JWT配置
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

### 前端配置
编辑 `AI-agent-frontend-naive/.env` 文件：
```env
# API配置
VITE_APP_BASE_API=http://localhost:8000
VITE_APP_PORT=3000

# 应用配置
VITE_APP_TITLE=Vue FastAPI Admin
VITE_APP_DESCRIPTION=现代化管理系统
```

## 🐳 Docker部署

### 使用Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./AI-agent-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/admin
    depends_on:
      - db

  frontend:
    build: ./AI-agent-frontend-naive
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=admin
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

启动命令：
```bash
docker-compose up -d
```

## 🌐 生产环境部署

### Nginx配置
```nginx
# /etc/nginx/sites-available/vue-fastapi-admin
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/vue-fastapi-admin/dist;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL配置（使用Let's Encrypt）
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```

### 进程管理（使用PM2）
```bash
# 安装PM2
npm install -g pm2

# 启动后端
pm2 start AI-agent-backend/main.py --name "fastapi-backend" --interpreter python3

# 启动前端构建
cd AI-agent-frontend-naive
pnpm build
pm2 serve dist 3000 --name "vue-frontend"

# 保存PM2配置
pm2 save
pm2 startup
```

## 📊 监控与日志

### 应用监控
```bash
# 查看PM2状态
pm2 status

# 查看日志
pm2 logs

# 监控资源使用
pm2 monit
```

### 数据库监控
```sql
-- 查看连接数
SELECT count(*) FROM pg_stat_activity;

-- 查看慢查询
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

## 🔒 安全配置

### 防火墙设置
```bash
# 开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 数据库安全
```sql
-- 创建专用数据库用户
CREATE USER admin_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE admin_db TO admin_user;
GRANT USAGE ON SCHEMA public TO admin_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO admin_user;
```

## 🚨 故障排除

### 常见问题

**1. 端口占用**
```bash
# 查看端口占用
lsof -i :8000
lsof -i :3000

# 杀死进程
kill -9 <PID>
```

**2. 数据库连接失败**
```bash
# 检查数据库状态
sudo systemctl status postgresql

# 重启数据库
sudo systemctl restart postgresql
```

**3. 前端构建失败**
```bash
# 清理缓存
pnpm store prune
rm -rf node_modules
pnpm install
```

**4. API请求失败**
```bash
# 检查后端日志
pm2 logs fastapi-backend

# 测试API连接
curl -X GET http://localhost:8000/docs
```

## 📈 性能优化

### 前端优化
- 启用Gzip压缩
- 配置CDN加速
- 图片懒加载
- 代码分割

### 后端优化
- 数据库索引优化
- Redis缓存
- 连接池配置
- 异步处理

### 数据库优化
```sql
-- 创建索引
CREATE INDEX idx_user_username ON users(username);
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_audit_log_created ON audit_logs(created_at);
```

## 📞 技术支持

如果在部署过程中遇到问题，请：

1. 查看日志文件
2. 运行测试脚本
3. 检查配置文件
4. 参考故障排除指南

**联系方式**：
- 邮箱：support@example.com
- 文档：https://docs.example.com
- 社区：https://community.example.com

---

**部署成功后，请访问：**
- 前端：http://your-domain.com
- API文档：http://your-domain.com/api/docs
- 默认账号：admin / 123456
