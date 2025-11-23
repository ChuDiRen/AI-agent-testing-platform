#!/bin/bash

# =============================================================================
# PostgreSQL 安装脚本
# 自动检测操作系统并安装配置 PostgreSQL
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置变量
POSTGRES_VERSION="15"
POSTGRES_PORT=5432
POSTGRES_PASSWORD="admin123456"
POSTGRES_DATA_DIR="${DATA_DIR:-/var/lib/postgresql/${POSTGRES_VERSION}/main}"
POSTGRES_LOG_DIR="${LOG_DIR:-/var/log/postgresql}"

log_info() {
    echo -e "${GREEN}[PostgreSQL]${NC} $1"
}

log_error() {
    echo -e "${RED}[PostgreSQL ERROR]${NC} $1"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙，开放端口 ${POSTGRES_PORT}..."
    
    # 检测防火墙类型并配置
    if command -v firewall-cmd &> /dev/null; then
        # firewalld (CentOS/RHEL/Fedora)
        log_info "检测到 firewalld"
        firewall-cmd --permanent --add-port=${POSTGRES_PORT}/tcp
        firewall-cmd --reload
        log_info "firewalld 端口 ${POSTGRES_PORT} 已开放"
    elif command -v ufw &> /dev/null; then
        # ufw (Ubuntu/Debian)
        log_info "检测到 ufw"
        ufw allow ${POSTGRES_PORT}/tcp
        log_info "ufw 端口 ${POSTGRES_PORT} 已开放"
    elif command -v iptables &> /dev/null; then
        # iptables (通用)
        log_info "检测到 iptables"
        iptables -I INPUT -p tcp --dport ${POSTGRES_PORT} -j ACCEPT
        # 保存 iptables 规则
        if command -v iptables-save &> /dev/null; then
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || \
            iptables-save > /etc/sysconfig/iptables 2>/dev/null || true
        fi
        log_info "iptables 端口 ${POSTGRES_PORT} 已开放"
    else
        log_info "未检测到防火墙或防火墙未启用"
    fi
}

# Ubuntu/Debian 安装
install_postgres_ubuntu() {
    log_info "在 Ubuntu/Debian 上安装 PostgreSQL..."
    apt-get update
    apt-get install -y postgresql postgresql-contrib
    systemctl start postgresql
    systemctl enable postgresql
    log_info "PostgreSQL 安装完成"
}

# CentOS/RHEL 安装
install_postgres_centos() {
    log_info "在 CentOS/RHEL 上安装 PostgreSQL..."
    yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-$(rpm -E %{rhel})-x86_64/pgdg-redhat-repo-latest.noarch.rpm
    if command -v dnf &> /dev/null; then
        dnf -qy module disable postgresql
    fi
    yum install -y postgresql${POSTGRES_VERSION}-server postgresql${POSTGRES_VERSION}-contrib
    /usr/pgsql-${POSTGRES_VERSION}/bin/postgresql-${POSTGRES_VERSION}-setup initdb
    systemctl start postgresql-${POSTGRES_VERSION}
    systemctl enable postgresql-${POSTGRES_VERSION}
    log_info "PostgreSQL 安装完成"
}

# macOS 安装
install_postgres_macos() {
    log_info "在 macOS 上安装 PostgreSQL..."
    if ! command -v brew &> /dev/null; then
        log_error "请先安装 Homebrew"
        exit 1
    fi
    brew install postgresql@${POSTGRES_VERSION}
    brew services start postgresql@${POSTGRES_VERSION}
    log_info "PostgreSQL 安装完成"
}

# 配置 PostgreSQL
configure_postgres() {
    log_info "配置 PostgreSQL..."
    
    if [ -f /etc/postgresql/${POSTGRES_VERSION}/main/postgresql.conf ]; then
        PG_CONF_DIR="/etc/postgresql/${POSTGRES_VERSION}/main"
    elif [ -f /var/lib/pgsql/${POSTGRES_VERSION}/data/postgresql.conf ]; then
        PG_CONF_DIR="/var/lib/pgsql/${POSTGRES_VERSION}/data"
    elif [ -f /usr/local/var/postgresql@${POSTGRES_VERSION}/postgresql.conf ]; then
        PG_CONF_DIR="/usr/local/var/postgresql@${POSTGRES_VERSION}"
    else
        log_error "找不到 PostgreSQL 配置文件"
        exit 1
    fi
    
    cp "$PG_CONF_DIR/postgresql.conf" "$PG_CONF_DIR/postgresql.conf.bak"
    cp "$PG_CONF_DIR/pg_hba.conf" "$PG_CONF_DIR/pg_hba.conf.bak"
    
    cat >> "$PG_CONF_DIR/postgresql.conf" <<EOF

listen_addresses = '*'
port = ${POSTGRES_PORT}
max_connections = 100
shared_buffers = 128MB
logging_collector = on
log_directory = '${POSTGRES_LOG_DIR}'
EOF
    
    cat > "$PG_CONF_DIR/pg_hba.conf" <<EOF
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             0.0.0.0/0               md5
host    all             all             ::1/128                 md5
EOF
    
    mkdir -p "$POSTGRES_LOG_DIR"
    if id "postgres" &>/dev/null; then
        chown -R postgres:postgres "$POSTGRES_LOG_DIR"
    fi
    
    systemctl restart postgresql || systemctl restart postgresql-${POSTGRES_VERSION}
    log_info "PostgreSQL 配置完成"
}

# 设置数据库
setup_database() {
    log_info "设置数据库..."
    sleep 3
    sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '${POSTGRES_PASSWORD}';"
    sudo -u postgres psql <<EOF
CREATE DATABASE testdb;
CREATE USER testuser WITH PASSWORD 'admin123456';
GRANT ALL PRIVILEGES ON DATABASE testdb TO testuser;
EOF
    log_info "数据库设置完成"
}

# 显示信息
show_connection_info() {
    echo ""
    echo "=========================================="
    echo "PostgreSQL 安装信息"
    echo "=========================================="
    echo "端口: ${POSTGRES_PORT}"
    echo "超级用户密码: ${POSTGRES_PASSWORD}"
    echo "测试数据库: testdb (用户: testuser, 密码: admin123456)"
    echo "连接命令: psql -h localhost -U postgres"
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始安装 PostgreSQL..."
    
    if [ "$OS_TYPE" == "ubuntu" ]; then
        install_postgres_ubuntu
    elif [ "$OS_TYPE" == "centos" ]; then
        install_postgres_centos
    elif [ "$OS_TYPE" == "macos" ]; then
        install_postgres_macos
    else
        log_error "不支持的操作系统"
        exit 1
    fi
    
    configure_postgres
    setup_database
    configure_firewall
    show_connection_info
    log_info "PostgreSQL 安装配置完成！"
}

if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
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
