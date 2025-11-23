#!/bin/bash

# =============================================================================
# Redis 安装脚本
# 自动检测操作系统并安装配置 Redis
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置变量
REDIS_VERSION="7.2.3"
REDIS_PORT=6379
REDIS_PASSWORD="admin123456"
REDIS_DATA_DIR="${DATA_DIR:-/var/lib/redis}"
REDIS_LOG_DIR="${LOG_DIR:-/var/log/redis}"

log_info() {
    echo -e "${GREEN}[Redis]${NC} $1"
}

log_error() {
    echo -e "${RED}[Redis ERROR]${NC} $1"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙，开放端口 ${REDIS_PORT}..."
    
    # 检测防火墙类型并配置
    if command -v firewall-cmd &> /dev/null; then
        # firewalld (CentOS/RHEL/Fedora)
        log_info "检测到 firewalld"
        firewall-cmd --permanent --add-port=${REDIS_PORT}/tcp
        firewall-cmd --reload
        log_info "firewalld 端口 ${REDIS_PORT} 已开放"
    elif command -v ufw &> /dev/null; then
        # ufw (Ubuntu/Debian)
        log_info "检测到 ufw"
        ufw allow ${REDIS_PORT}/tcp
        log_info "ufw 端口 ${REDIS_PORT} 已开放"
    elif command -v iptables &> /dev/null; then
        # iptables (通用)
        log_info "检测到 iptables"
        iptables -I INPUT -p tcp --dport ${REDIS_PORT} -j ACCEPT
        # 保存 iptables 规则
        if command -v iptables-save &> /dev/null; then
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || \
            iptables-save > /etc/sysconfig/iptables 2>/dev/null || true
        fi
        log_info "iptables 端口 ${REDIS_PORT} 已开放"
    else
        log_info "未检测到防火墙或防火墙未启用"
    fi
}

# Ubuntu/Debian 安装
install_redis_ubuntu() {
    log_info "在 Ubuntu/Debian 上安装 Redis..."
    
    apt-get update
    apt-get install -y redis-server
    
    systemctl start redis-server
    systemctl enable redis-server
    
    log_info "Redis 安装完成"
}

# CentOS/RHEL 安装
install_redis_centos() {
    log_info "在 CentOS/RHEL 上安装 Redis..."
    
    yum install -y epel-release
    yum install -y redis
    
    systemctl start redis
    systemctl enable redis
    
    log_info "Redis 安装完成"
}

# macOS 安装
install_redis_macos() {
    log_info "在 macOS 上安装 Redis..."
    
    if ! command -v brew &> /dev/null; then
        log_error "请先安装 Homebrew"
        exit 1
    fi
    
    brew install redis
    
    brew services start redis
    
    log_info "Redis 安装完成"
}

# 配置 Redis
configure_redis() {
    log_info "配置 Redis..."
    
    # 备份原配置文件
    if [ -f /etc/redis/redis.conf ]; then
        cp /etc/redis/redis.conf /etc/redis/redis.conf.bak
        REDIS_CONF="/etc/redis/redis.conf"
    elif [ -f /etc/redis.conf ]; then
        cp /etc/redis.conf /etc/redis.conf.bak
        REDIS_CONF="/etc/redis.conf"
    elif [ -f /usr/local/etc/redis.conf ]; then
        cp /usr/local/etc/redis.conf /usr/local/etc/redis.conf.bak
        REDIS_CONF="/usr/local/etc/redis.conf"
    else
        log_error "找不到 Redis 配置文件"
        exit 1
    fi
    
    # 创建自定义配置
    cat > "$REDIS_CONF" <<EOF
# Redis 配置文件

# 网络设置
bind 0.0.0.0
port ${REDIS_PORT}
protected-mode yes
tcp-backlog 511
timeout 0
tcp-keepalive 300

# 通用设置
daemonize yes
supervised systemd
pidfile /var/run/redis/redis-server.pid
loglevel notice
logfile ${REDIS_LOG_DIR}/redis.log
databases 16

# 持久化设置
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir ${REDIS_DATA_DIR}

# 安全设置
requirepass ${REDIS_PASSWORD}

# 内存管理
maxmemory 256mb
maxmemory-policy allkeys-lru

# AOF 持久化
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# 慢查询日志
slowlog-log-slower-than 10000
slowlog-max-len 128

# 客户端输出缓冲限制
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
EOF
    
    # 创建必要的目录
    mkdir -p "$REDIS_DATA_DIR"
    mkdir -p "$REDIS_LOG_DIR"
    mkdir -p /var/run/redis
    
    # 设置权限
    if id "redis" &>/dev/null; then
        chown -R redis:redis "$REDIS_DATA_DIR"
        chown -R redis:redis "$REDIS_LOG_DIR"
        chown -R redis:redis /var/run/redis
    fi
    
    # 重启 Redis
    systemctl restart redis-server || systemctl restart redis
    
    log_info "Redis 配置完成"
}

# 测试 Redis 连接
test_redis_connection() {
    log_info "测试 Redis 连接..."
    
    sleep 2
    
    if redis-cli -a "${REDIS_PASSWORD}" ping | grep -q "PONG"; then
        log_info "Redis 连接测试成功"
    else
        log_error "Redis 连接测试失败"
        exit 1
    fi
}

# 显示连接信息
show_connection_info() {
    echo ""
    echo "=========================================="
    echo "Redis 安装信息"
    echo "=========================================="
    echo "端口: ${REDIS_PORT}"
    echo "密码: ${REDIS_PASSWORD}"
    echo "数据目录: ${REDIS_DATA_DIR}"
    echo "日志目录: ${REDIS_LOG_DIR}"
    echo ""
    echo "连接命令: redis-cli -a '${REDIS_PASSWORD}'"
    echo "测试命令: redis-cli -a '${REDIS_PASSWORD}' ping"
    echo ""
    echo "Python 连接示例:"
    echo "  import redis"
    echo "  r = redis.Redis(host='localhost', port=${REDIS_PORT}, password='${REDIS_PASSWORD}', decode_responses=True)"
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始安装 Redis..."
    
    # 检测操作系统并安装
    if [ "$OS_TYPE" == "ubuntu" ]; then
        install_redis_ubuntu
    elif [ "$OS_TYPE" == "centos" ]; then
        install_redis_centos
    elif [ "$OS_TYPE" == "macos" ]; then
        install_redis_macos
    else
        log_error "不支持的操作系统"
        exit 1
    fi
    
    # 配置 Redis
    configure_redis
    
    # 测试连接
    test_redis_connection
    
    # 配置防火墙
    configure_firewall
    
    # 显示连接信息
    show_connection_info
    
    log_info "Redis 安装配置完成！"
}

# 如果直接运行此脚本
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    # 检测操作系统
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
    
    main "$@"
fi
