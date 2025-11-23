#!/bin/bash

# =============================================================================
# RabbitMQ Docker 部署脚本
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$BASE_DIR/database-data/rabbitmq"

CONTAINER_NAME="rabbitmq"
IMAGE="rabbitmq:3.12-management-alpine"
AMQP_PORT="5672"
MGMT_PORT="15672"
USER="admin"
PASSWORD="admin123456"

log_info() { echo -e "${GREEN}[RabbitMQ]${NC} $1"; }
log_error() { echo -e "${RED}[RabbitMQ ERROR]${NC} $1"; }

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
log_info "启动 RabbitMQ 容器..."
docker run -d \
  --name $CONTAINER_NAME \
  --restart always \
  -p $AMQP_PORT:5672 \
  -p $MGMT_PORT:15672 \
  -e RABBITMQ_DEFAULT_USER=$USER \
  -e RABBITMQ_DEFAULT_PASS=$PASSWORD \
  -e TZ=Asia/Shanghai \
  -v "$DATA_DIR":/var/lib/rabbitmq \
  $IMAGE

# 开放防火墙端口
open_firewall_port $AMQP_PORT
open_firewall_port $MGMT_PORT

# 等待启动
sleep 10

# 检查状态
if docker ps | grep -q $CONTAINER_NAME; then
    log_info "✓ RabbitMQ 部署成功"
    echo ""
    echo "连接信息:"
    echo "  AMQP 端口: $AMQP_PORT"
    echo "  本地管理界面: http://localhost:$MGMT_PORT"
    echo "  远程管理界面: http://<服务器IP>:$MGMT_PORT"
    echo "  防火墙端口: $AMQP_PORT, $MGMT_PORT 已开放"
    echo "  用户名: $USER"
    echo "  密码: $PASSWORD"
else
    log_error "✗ RabbitMQ 启动失败"
    docker logs $CONTAINER_NAME
    exit 1
fi
