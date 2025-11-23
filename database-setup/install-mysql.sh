#!/bin/bash

# =============================================================================
# MySQL 安装脚本
# 自动检测操作系统并安装配置 MySQL
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置变量
MYSQL_ROOT_PASSWORD="admin123456"
MYSQL_PORT=3306
MYSQL_DATA_DIR="${DATA_DIR:-/var/lib/mysql}"
MYSQL_LOG_DIR="${LOG_DIR:-/var/log/mysql}"

log_info() {
    echo -e "${GREEN}[MySQL]${NC} $1"
}

log_error() {
    echo -e "${RED}[MySQL ERROR]${NC} $1"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙，开放端口 ${MYSQL_PORT}..."
    
    # 检测防火墙类型并配置
    if command -v firewall-cmd &> /dev/null; then
        # firewalld (CentOS/RHEL/Fedora)
        log_info "检测到 firewalld"
        firewall-cmd --permanent --add-port=${MYSQL_PORT}/tcp
        firewall-cmd --reload
        log_info "firewalld 端口 ${MYSQL_PORT} 已开放"
    elif command -v ufw &> /dev/null; then
        # ufw (Ubuntu/Debian)
        log_info "检测到 ufw"
        ufw allow ${MYSQL_PORT}/tcp
        log_info "ufw 端口 ${MYSQL_PORT} 已开放"
    elif command -v iptables &> /dev/null; then
        # iptables (通用)
        log_info "检测到 iptables"
        iptables -I INPUT -p tcp --dport ${MYSQL_PORT} -j ACCEPT
        # 保存 iptables 规则
        if command -v iptables-save &> /dev/null; then
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || \
            iptables-save > /etc/sysconfig/iptables 2>/dev/null || true
        fi
        log_info "iptables 端口 ${MYSQL_PORT} 已开放"
    else
        log_info "未检测到防火墙或防火墙未启用"
    fi
}

# Ubuntu/Debian 安装
install_mysql_ubuntu() {
    log_info "在 Ubuntu/Debian 上安装 MySQL..."
    
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server
    
    systemctl start mysql
    systemctl enable mysql
    
    # 设置 root 密码
    mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${MYSQL_ROOT_PASSWORD}';"
    mysql -e "FLUSH PRIVILEGES;"
    
    log_info "MySQL 安装完成"
}

# CentOS/RHEL 安装
install_mysql_centos() {
    log_info "在 CentOS/RHEL 上安装 MySQL..."
    
    yum install -y mysql-server
    
    systemctl start mysqld
    systemctl enable mysqld
    
    # 获取临时密码
    TEMP_PASSWORD=$(grep 'temporary password' /var/log/mysqld.log | awk '{print $NF}')
    
    # 修改 root 密码
    mysql --connect-expired-password -uroot -p"${TEMP_PASSWORD}" -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}';"
    
    log_info "MySQL 安装完成"
}

# macOS 安装
install_mysql_macos() {
    log_info "在 macOS 上安装 MySQL..."
    
    if ! command -v brew &> /dev/null; then
        log_error "请先安装 Homebrew"
        exit 1
    fi
    
    brew install mysql
    
    brew services start mysql
    
    # 设置 root 密码
    mysql -uroot -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}';"
    
    log_info "MySQL 安装完成"
}

# 配置 MySQL
configure_mysql() {
    log_info "配置 MySQL..."
    
    # 创建配置文件
    cat > /etc/mysql/conf.d/custom.cnf <<EOF
[mysqld]
# 基本设置
port = ${MYSQL_PORT}
datadir = ${MYSQL_DATA_DIR}
socket = /var/run/mysqld/mysqld.sock

# 字符集设置
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# 连接设置
max_connections = 200
max_connect_errors = 100

# 日志设置
log_error = ${MYSQL_LOG_DIR}/error.log
slow_query_log = 1
slow_query_log_file = ${MYSQL_LOG_DIR}/slow.log
long_query_time = 2

# InnoDB 设置
innodb_buffer_pool_size = 256M
innodb_log_file_size = 64M
innodb_flush_log_at_trx_commit = 2

[client]
default-character-set = utf8mb4
EOF
    
    # 重启 MySQL
    systemctl restart mysql || systemctl restart mysqld
    
    log_info "MySQL 配置完成"
}

# 创建测试数据库
create_test_database() {
    log_info "创建测试数据库..."
    
    mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" <<EOF
CREATE DATABASE IF NOT EXISTS testdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'testuser'@'%' IDENTIFIED BY 'admin123456';
GRANT ALL PRIVILEGES ON testdb.* TO 'testuser'@'%';
FLUSH PRIVILEGES;
EOF
    
    log_info "测试数据库创建完成"
    log_info "数据库: testdb, 用户: testuser, 密码: admin123456"
}

# 显示连接信息
show_connection_info() {
    echo ""
    echo "=========================================="
    echo "MySQL 安装信息"
    echo "=========================================="
    echo "端口: ${MYSQL_PORT}"
    echo "Root 密码: ${MYSQL_ROOT_PASSWORD}"
    echo "数据目录: ${MYSQL_DATA_DIR}"
    echo "日志目录: ${MYSQL_LOG_DIR}"
    echo ""
    echo "测试数据库: testdb"
    echo "测试用户: testuser"
    echo "测试密码: admin123456"
    echo ""
    echo "连接命令: mysql -uroot -p'${MYSQL_ROOT_PASSWORD}'"
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始安装 MySQL..."
    
    # 检测操作系统并安装
    if [ "$OS_TYPE" == "ubuntu" ]; then
        install_mysql_ubuntu
    elif [ "$OS_TYPE" == "centos" ]; then
        install_mysql_centos
    elif [ "$OS_TYPE" == "macos" ]; then
        install_mysql_macos
    else
        log_error "不支持的操作系统"
        exit 1
    fi
    
    # 配置 MySQL
    configure_mysql
    
    # 创建测试数据库
    create_test_database
    
    # 配置防火墙
    configure_firewall
    
    # 显示连接信息
    show_connection_info
    
    log_info "MySQL 安装配置完成！"
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
