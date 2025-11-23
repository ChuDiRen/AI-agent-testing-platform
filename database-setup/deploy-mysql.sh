#!/bin/bash

# =============================================================================
# MySQL Docker 部署脚本
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$BASE_DIR/database-data/mysql"
LOG_DIR="$BASE_DIR/database-logs/mysql"

CONTAINER_NAME="mysql"
IMAGE="mysql:8.0"
PORT="3306"
ROOT_PASSWORD="admin123456"

log_info() { echo -e "${GREEN}[MySQL]${NC} $1"; }
log_error() { echo -e "${RED}[MySQL ERROR]${NC} $1"; }

# 开放防火墙端口
open_firewall_port() {
    local port=$1
    
    # 检测防火墙类型并开放端口
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
log_info "启动 MySQL 容器..."
docker run -d \
  --name $CONTAINER_NAME \
  --restart always \
  -p $PORT:3306 \
  -e MYSQL_ROOT_PASSWORD=$ROOT_PASSWORD \
  -e MYSQL_DATABASE=testdb \
  -e MYSQL_USER=testuser \
  -e MYSQL_PASSWORD=admin123456 \
  -e TZ=Asia/Shanghai \
  -v "$DATA_DIR":/var/lib/mysql \
  -v "$LOG_DIR":/var/log/mysql \
  $IMAGE \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci

# 开放防火墙端口
open_firewall_port $PORT

# 等待启动
log_info "等待 MySQL 启动..."
sleep 10

# 配置远程访问权限
log_info "配置远程访问权限..."
docker exec $CONTAINER_NAME mysql -uroot -p"$ROOT_PASSWORD" -e "
    USE mysql;
    CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '$ROOT_PASSWORD';
    GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
    FLUSH PRIVILEGES;
" 2>/dev/null || log_info "远程访问权限已配置或跳过"

# 检查状态
if docker ps | grep -q $CONTAINER_NAME; then
    log_info "✓ MySQL 部署成功"
    echo ""
    echo "连接信息:"
    echo "  端口: $PORT"
    echo "  Root 密码: $ROOT_PASSWORD"
    echo "  测试库: testdb"
    echo "  测试用户: testuser / admin123456"
    echo "  本地连接: mysql -h 127.0.0.1 -uroot -p'$ROOT_PASSWORD'"
    echo "  远程连接: mysql -h <服务器IP> -uroot -p'$ROOT_PASSWORD'"
    echo "  防火墙端口: $PORT 已开放"
else
    log_error "✗ MySQL 启动失败"
    docker logs $CONTAINER_NAME
    exit 1
fi
