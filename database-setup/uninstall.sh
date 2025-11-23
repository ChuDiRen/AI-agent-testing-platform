#!/bin/bash

# =============================================================================
# 数据库卸载脚本
# 卸载 MySQL、Redis、PostgreSQL
# =============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

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
            elif [[ "$OS" == "centos" ]] || [[ "$OS" == "rhel" ]]; then
                OS_TYPE="centos"
            fi
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="macos"
    fi
}

# 卸载 MySQL
uninstall_mysql() {
    log_warn "卸载 MySQL..."
    
    if [ "$OS_TYPE" == "ubuntu" ]; then
        systemctl stop mysql || true
        apt-get remove --purge -y mysql-server mysql-client mysql-common
        apt-get autoremove -y
        apt-get autoclean
        rm -rf /etc/mysql /var/lib/mysql
    elif [ "$OS_TYPE" == "centos" ]; then
        systemctl stop mysqld || true
        yum remove -y mysql-server
        rm -rf /var/lib/mysql
    elif [ "$OS_TYPE" == "macos" ]; then
        brew services stop mysql || true
        brew uninstall mysql
        rm -rf /usr/local/var/mysql
    fi
    
    log_info "MySQL 卸载完成"
}

# 卸载 Redis
uninstall_redis() {
    log_warn "卸载 Redis..."
    
    if [ "$OS_TYPE" == "ubuntu" ]; then
        systemctl stop redis-server || true
        apt-get remove --purge -y redis-server
        apt-get autoremove -y
        rm -rf /etc/redis /var/lib/redis
    elif [ "$OS_TYPE" == "centos" ]; then
        systemctl stop redis || true
        yum remove -y redis
        rm -rf /var/lib/redis
    elif [ "$OS_TYPE" == "macos" ]; then
        brew services stop redis || true
        brew uninstall redis
    fi
    
    log_info "Redis 卸载完成"
}

# 卸载 PostgreSQL
uninstall_postgres() {
    log_warn "卸载 PostgreSQL..."
    
    if [ "$OS_TYPE" == "ubuntu" ]; then
        systemctl stop postgresql || true
        apt-get remove --purge -y postgresql postgresql-contrib
        apt-get autoremove -y
        rm -rf /etc/postgresql /var/lib/postgresql
    elif [ "$OS_TYPE" == "centos" ]; then
        systemctl stop postgresql-15 || true
        yum remove -y postgresql15-server
        rm -rf /var/lib/pgsql
    elif [ "$OS_TYPE" == "macos" ]; then
        brew services stop postgresql@15 || true
        brew uninstall postgresql@15
    fi
    
    log_info "PostgreSQL 卸载完成"
}

# 卸载 MinIO
uninstall_minio() {
    log_warn "卸载 MinIO..."
    
    if [ "$OS_TYPE" == "ubuntu" ] || [ "$OS_TYPE" == "centos" ]; then
        systemctl stop minio || true
        systemctl disable minio || true
        rm -f /etc/systemd/system/minio.service
        rm -f /usr/local/bin/minio
        rm -f /usr/local/bin/mc
        rm -rf /var/lib/minio
        rm -rf /etc/minio
        userdel minio || true
    elif [ "$OS_TYPE" == "macos" ]; then
        launchctl unload ~/Library/LaunchAgents/io.min.minio.plist || true
        rm -f ~/Library/LaunchAgents/io.min.minio.plist
        brew uninstall minio || true
    fi
    
    log_info "MinIO 卸载完成"
}

# 卸载 RabbitMQ
uninstall_rabbitmq() {
    log_warn "卸载 RabbitMQ..."
    
    if [ "$OS_TYPE" == "ubuntu" ]; then
        systemctl stop rabbitmq-server || true
        apt-get remove --purge -y rabbitmq-server erlang-base
        apt-get autoremove -y
        rm -rf /etc/rabbitmq /var/lib/rabbitmq
    elif [ "$OS_TYPE" == "centos" ]; then
        systemctl stop rabbitmq-server || true
        yum remove -y rabbitmq-server erlang
        rm -rf /etc/rabbitmq /var/lib/rabbitmq
    elif [ "$OS_TYPE" == "macos" ]; then
        brew services stop rabbitmq || true
        brew uninstall rabbitmq
    fi
    
    log_info "RabbitMQ 卸载完成"
}

# 主函数
main() {
    echo "=========================================="
    echo "  服务卸载脚本"
    echo "=========================================="
    echo ""
    
    log_warn "警告: 此操作将删除所有服务及其数据！"
    log_info "自动执行卸载，无需确认"
    
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要 root 权限"
        exit 1
    fi
    
    detect_os
    
    uninstall_mysql
    uninstall_redis
    uninstall_postgres
    uninstall_minio
    uninstall_rabbitmq
    
    log_info "所有服务已卸载"
}

main "$@"
