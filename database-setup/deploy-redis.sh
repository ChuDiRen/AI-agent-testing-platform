#!/bin/bash

# =============================================================================
# Redis Docker 部署脚本
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$BASE_DIR/database-data/redis"

CONTAINER_NAME="redis"
IMAGE="redis:7-alpine"
PORT="6379"
PASSWORD="admin123456"

log_info() { echo -e "${GREEN}[Redis]${NC} $1"; }
log_error() { echo -e "${RED}[Redis ERROR]${NC} $1"; }

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
log_info "启动 Redis 容器..."
docker run -d \
  --name $CONTAINER_NAME \
  --restart always \
  -p $PORT:6379 \
  -e TZ=Asia/Shanghai \
  -v "$DATA_DIR":/data \
  $IMAGE \
  redis-server --requirepass $PASSWORD --appendonly yes

# 开放防火墙端口
open_firewall_port $PORT

# 等待启动
sleep 3

# 检查状态
if docker ps | grep -q $CONTAINER_NAME; then
    log_info "✓ Redis 部署成功"
    echo ""
    echo "连接信息:"
    echo "  端口: $PORT"
    echo "  密码: $PASSWORD"
    echo "  本地连接: redis-cli -h 127.0.0.1 -a '$PASSWORD'"
    echo "  远程连接: redis-cli -h <服务器IP> -a '$PASSWORD'"
    echo "  防火墙端口: $PORT 已开放"
else
    log_error "✗ Redis 启动失败"
    docker logs $CONTAINER_NAME
    exit 1
fi
