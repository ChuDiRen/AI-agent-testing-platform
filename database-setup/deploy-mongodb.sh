#!/bin/bash

# =============================================================================
# MongoDB Docker 部署脚本
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$BASE_DIR/database-data/mongodb"
LOG_DIR="$BASE_DIR/database-logs/mongodb"

CONTAINER_NAME="mongodb"
IMAGE="mongo:7.0"
PORT="27017"
ROOT_USER="root"
ROOT_PASSWORD="admin123456"

log_info() { echo -e "${GREEN}[MongoDB]${NC} $1"; }
log_error() { echo -e "${RED}[MongoDB ERROR]${NC} $1"; }

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
mkdir -p "$DATA_DIR" "$LOG_DIR"

# 停止并删除旧容器
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# 拉取镜像
log_info "拉取镜像: $IMAGE"
docker pull $IMAGE

# 启动容器
log_info "启动 MongoDB 容器..."
docker run -d \
  --name $CONTAINER_NAME \
  --restart always \
  -p $PORT:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=$ROOT_USER \
  -e MONGO_INITDB_ROOT_PASSWORD=$ROOT_PASSWORD \
  -e TZ=Asia/Shanghai \
  -v "$DATA_DIR":/data/db \
  -v "$LOG_DIR":/var/log/mongodb \
  $IMAGE

# 开放防火墙端口
open_firewall_port $PORT

# 等待启动
log_info "等待 MongoDB 启动..."
sleep 5

# 创建测试数据库和用户
log_info "创建测试数据库和用户..."
docker exec $CONTAINER_NAME mongosh -u "$ROOT_USER" -p "$ROOT_PASSWORD" --authenticationDatabase admin --eval "
    db = db.getSiblingDB('testdb');
    db.createUser({
        user: 'testuser',
        pwd: 'admin123456',
        roles: [{ role: 'readWrite', db: 'testdb' }]
    });
    db.test_collection.insertOne({ init: true, created_at: new Date() });
" 2>/dev/null || log_info "测试用户已存在或跳过"

# 检查状态
if docker ps | grep -q $CONTAINER_NAME; then
    log_info "✓ MongoDB 部署成功"
    echo ""
    echo "连接信息:"
    echo "  端口: $PORT"
    echo "  Root 用户: $ROOT_USER"
    echo "  Root 密码: $ROOT_PASSWORD"
    echo "  测试库: testdb"
    echo "  测试用户: testuser / admin123456"
    echo "  本地连接: mongosh mongodb://127.0.0.1:$PORT -u $ROOT_USER -p '$ROOT_PASSWORD' --authenticationDatabase admin"
    echo "  远程连接: mongosh mongodb://<服务器IP>:$PORT -u $ROOT_USER -p '$ROOT_PASSWORD' --authenticationDatabase admin"
    echo "  连接字符串: mongodb://$ROOT_USER:$ROOT_PASSWORD@127.0.0.1:$PORT/?authSource=admin"
    echo "  防火墙端口: $PORT 已开放"
else
    log_error "✗ MongoDB 启动失败"
    docker logs $CONTAINER_NAME
    exit 1
fi
