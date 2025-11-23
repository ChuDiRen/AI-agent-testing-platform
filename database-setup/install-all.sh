#!/bin/bash

# =============================================================================
# 数据库一键安装脚本 - 主脚本
# 支持 MySQL、Redis、PostgreSQL 的自动安装和配置
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$BASE_DIR/database-data"
LOG_DIR="$BASE_DIR/database-logs"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
            if [[ "$OS" == "ubuntu" ]] || [[ "$OS" == "debian" ]]; then
                OS_TYPE="ubuntu"
            elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]] || [[ "$OS" == "fedora" ]]; then
                OS_TYPE="centos"
            else
                OS_TYPE="unknown"
            fi
        else
            OS_TYPE="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="macos"
    else
        OS_TYPE="unknown"
    fi
    
    log_info "检测到操作系统: $OS_TYPE"
}

# 创建必要的目录
create_directories() {
    log_info "创建数据和日志目录..."
    
    mkdir -p "$DATA_DIR/mysql"
    mkdir -p "$DATA_DIR/redis"
    mkdir -p "$DATA_DIR/postgres"
    
    mkdir -p "$LOG_DIR/mysql"
    mkdir -p "$LOG_DIR/redis"
    mkdir -p "$LOG_DIR/postgres"
    
    log_info "目录创建完成"
}

# 检查是否以root权限运行
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要 root 权限运行"
        log_info "请使用: sudo $0"
        exit 1
    fi
}

# 主函数
main() {
    echo "=========================================="
    echo "  基础服务一键安装脚本"
    echo "  MySQL + Redis + PostgreSQL"
    echo "  MinIO + RabbitMQ"
    echo "=========================================="
    echo ""
    
    # 检查root权限
    check_root
    
    # 检测操作系统
    detect_os
    
    if [ "$OS_TYPE" == "unknown" ]; then
        log_error "不支持的操作系统"
        exit 1
    fi
    
    # 创建目录
    create_directories
    
    # 安装 MySQL
    log_info "开始安装 MySQL..."
    bash "$SCRIPT_DIR/install-mysql.sh"
    
    # 安装 Redis
    log_info "开始安装 Redis..."
    bash "$SCRIPT_DIR/install-redis.sh"
    
    # 安装 PostgreSQL
    log_info "开始安装 PostgreSQL..."
    bash "$SCRIPT_DIR/install-postgres.sh"
    
    # 安装 MinIO
    log_info "开始安装 MinIO..."
    bash "$SCRIPT_DIR/install-minio.sh"
    
    # 安装 RabbitMQ
    log_info "开始安装 RabbitMQ..."
    bash "$SCRIPT_DIR/install-rabbitmq.sh"
    
    echo ""
    echo "=========================================="
    log_info "所有服务安装完成！"
    echo "=========================================="
    echo ""
    echo "数据目录: $DATA_DIR"
    echo "日志目录: $LOG_DIR"
    echo ""
    echo "服务端口信息:"
    echo "  MySQL: 3306"
    echo "  Redis: 6379"
    echo "  PostgreSQL: 5432"
    echo "  MinIO API: 9000"
    echo "  MinIO Console: 9001"
    echo "  RabbitMQ AMQP: 5672"
    echo "  RabbitMQ Management: 15672"
    echo ""
    echo "统一密码: admin123456"
    echo ""
    log_info "请查看各服务的配置文件以获取详细连接信息"
}

main "$@"
