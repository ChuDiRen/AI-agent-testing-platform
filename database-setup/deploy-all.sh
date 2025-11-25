#!/bin/bash

# =============================================================================
# 一键部署所有服务（Docker 版本）
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

echo ""
echo "=========================================="
echo "  一键部署所有服务"
echo "=========================================="
echo ""
echo "将部署以下服务："
echo "  - MySQL 8.0"
echo "  - Redis 7"
echo "  - PostgreSQL 14"
echo "  - MongoDB 7.0"
echo "  - MinIO"
echo "  - RabbitMQ 3.12"
echo ""
echo "统一密码: admin123456"
echo ""
echo "=========================================="
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "Docker 未安装，请先运行: sudo bash install-docker.sh"
    exit 1
fi

# 询问确认
read -p "确认开始部署？[y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "取消部署"
    exit 0
fi

# 部署各个服务
log_step "部署 MySQL..."
bash "$SCRIPT_DIR/deploy-mysql.sh"

echo ""
log_step "部署 Redis..."
bash "$SCRIPT_DIR/deploy-redis.sh"

echo ""
log_step "部署 PostgreSQL..."
bash "$SCRIPT_DIR/deploy-postgres.sh"

echo ""
log_step "部署 MongoDB..."
bash "$SCRIPT_DIR/deploy-mongodb.sh"

echo ""
log_step "部署 MinIO..."
bash "$SCRIPT_DIR/deploy-minio.sh"

echo ""
log_step "部署 RabbitMQ..."
bash "$SCRIPT_DIR/deploy-rabbitmq.sh"

echo ""
echo "=========================================="
log_info "所有服务部署完成！"
echo "=========================================="
echo ""
echo "查看运行状态: docker ps"
echo "查看日志: docker logs [容器名]"
echo ""
