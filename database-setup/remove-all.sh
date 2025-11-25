#!/bin/bash

# =============================================================================
# 卸载所有服务
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

echo ""
echo "=========================================="
echo "  卸载所有服务"
echo "=========================================="
echo ""
log_warn "此操作将删除所有容器（数据保留）"
echo ""

read -p "确认卸载？[y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "取消卸载"
    exit 0
fi

# 停止并删除容器
containers=("mysql" "redis" "postgres" "mongodb" "minio" "rabbitmq")

for container in "${containers[@]}"; do
    if docker ps -a | grep -q "$container"; then
        log_info "删除 $container..."
        docker stop "$container" 2>/dev/null || true
        docker rm "$container" 2>/dev/null || true
    fi
done

log_info "所有服务已卸载"
echo ""
echo "数据目录保留在: ../database-data/"
echo "如需删除数据: rm -rf ../database-data/"
echo ""
