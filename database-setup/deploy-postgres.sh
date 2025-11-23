#!/bin/bash

# =============================================================================
# PostgreSQL Docker 部署脚本
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$BASE_DIR/database-data/postgres"

CONTAINER_NAME="postgres"
IMAGE="postgres:14-alpine"
PORT="5432"
PASSWORD="admin123456"

log_info() { echo -e "${GREEN}[PostgreSQL]${NC} $1"; }
log_error() { echo -e "${RED}[PostgreSQL ERROR]${NC} $1"; }

# 开放防火墙端口
open_firewall_port() {
    local port=$1
    
    if command -v firewall-cmd &> /dev/null && systemctl is-active --quiet firewalld; then
        log_info "开放防火墙端口 $port (firewalld)..."
        firewall-cmd --permanent --add-port=${port}/tcp 2>/dev/null || true
        firewall-cmd --reload 2>/dev/null || true
    elif command -v ufw &> /dev/null && ufw status | grep -q "Status: active"; then
        log_info "开放防火墙端口 $port (ufw)..."
        ufw allow ${port}/tcp 2>/dev/null || true
    else
        log_info "未检测到活动的防火墙或已开放"
    fi
}

# 创建目录
mkdir -p "$DATA_DIR"

# 停止并删除旧容器
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 拉取镜像
log_info "拉取镜像: $IMAGE"
docker pull $IMAGE

# 启动容器
log_info "启动 PostgreSQL 容器..."
docker run -d \
  --name $CONTAINER_NAME \
  --restart always \
  -p $PORT:5432 \
  -e POSTGRES_PASSWORD=$PASSWORD \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=testdb \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -e TZ=Asia/Shanghai \
  -v "$DATA_DIR":/var/lib/postgresql/data \
  $IMAGE \
  -c listen_addresses='*'

# 开放防火墙端口
open_firewall_port $PORT

# 等待启动
sleep 5

# 配置远程访问权限
log_info "配置远程访问权限..."
docker exec $CONTAINER_NAME psql -U postgres -c "ALTER USER postgres WITH PASSWORD '$PASSWORD';" 2>/dev/null || true

# 配置 pg_hba.conf 允许远程连接
docker exec $CONTAINER_NAME sh -c "echo 'host all all 0.0.0.0/0 md5' >> /var/lib/postgresql/data/pgdata/pg_hba.conf" 2>/dev/null || true
docker restart $CONTAINER_NAME > /dev/null 2>&1
sleep 3

# 检查状态
if docker ps | grep -q $CONTAINER_NAME; then
    log_info "✓ PostgreSQL 部署成功"
    echo ""
    echo "连接信息:"
    echo "  端口: $PORT"
    echo "  用户: postgres"
    echo "  密码: $PASSWORD"
    echo "  数据库: testdb"
    echo "  本地连接: psql -h 127.0.0.1 -U postgres -d testdb"
    echo "  远程连接: psql -h <服务器IP> -U postgres -d testdb"
    echo "  防火墙端口: $PORT 已开放"
else
    log_error "✗ PostgreSQL 启动失败"
    docker logs $CONTAINER_NAME
    exit 1
fi
