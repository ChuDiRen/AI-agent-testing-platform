#!/bin/bash

# =============================================================================
# MinIO Docker 部署脚本
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$BASE_DIR/database-data/minio"

CONTAINER_NAME="minio"
IMAGE="minio/minio:RELEASE.2024-06-13T22-53-53Z"
API_PORT="9000"
CONSOLE_PORT="9001"
ROOT_USER="admin"
ROOT_PASSWORD="admin123456"

log_info() { echo -e "${GREEN}[MinIO]${NC} $1"; }
log_error() { echo -e "${RED}[MinIO ERROR]${NC} $1"; }

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
log_info "启动 MinIO 容器..."
docker run -d \
  --name $CONTAINER_NAME \
  --restart always \
  -p $API_PORT:9000 \
  -p $CONSOLE_PORT:9001 \
  -e MINIO_ROOT_USER=$ROOT_USER \
  -e MINIO_ROOT_PASSWORD=$ROOT_PASSWORD \
  -e TZ=Asia/Shanghai \
  -v "$DATA_DIR":/data \
  $IMAGE \
  server /data --console-address ":9001"

# 开放防火墙端口
open_firewall_port $API_PORT
open_firewall_port $CONSOLE_PORT

# 等待启动
sleep 5

# 检查状态
if docker ps | grep -q $CONTAINER_NAME; then
    log_info "✓ MinIO 部署成功"
    echo ""
    echo "连接信息:"
    echo "  API 端口: $API_PORT"
    echo "  本地控制台: http://localhost:$CONSOLE_PORT"
    echo "  远程控制台: http://<服务器IP>:$CONSOLE_PORT"
    echo "  防火墙端口: $API_PORT, $CONSOLE_PORT 已开放"
    echo "  用户名: $ROOT_USER"
    echo "  密码: $ROOT_PASSWORD"
else
    log_error "✗ MinIO 启动失败"
    docker logs $CONTAINER_NAME
    exit 1
fi
