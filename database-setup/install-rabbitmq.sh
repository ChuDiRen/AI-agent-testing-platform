#!/bin/bash

# =============================================================================
# RabbitMQ 安装脚本
# 自动检测操作系统并安装配置 RabbitMQ 消息队列
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置变量
RABBITMQ_VERSION="3.12"
RABBITMQ_PORT=5672
RABBITMQ_MANAGEMENT_PORT=15672
RABBITMQ_USER="admin"
RABBITMQ_PASSWORD="admin123456"
RABBITMQ_VHOST="/"

log_info() {
    echo -e "${GREEN}[RabbitMQ]${NC} $1"
}

log_error() {
    echo -e "${RED}[RabbitMQ ERROR]${NC} $1"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙，开放端口 ${RABBITMQ_PORT} 和 ${RABBITMQ_MANAGEMENT_PORT}..."
    
    # 检测防火墙类型并配置
    if command -v firewall-cmd &> /dev/null; then
        # firewalld (CentOS/RHEL/Fedora)
        log_info "检测到 firewalld"
        firewall-cmd --permanent --add-port=${RABBITMQ_PORT}/tcp
        firewall-cmd --permanent --add-port=${RABBITMQ_MANAGEMENT_PORT}/tcp
        firewall-cmd --reload
        log_info "firewalld 端口 ${RABBITMQ_PORT} 和 ${RABBITMQ_MANAGEMENT_PORT} 已开放"
    elif command -v ufw &> /dev/null; then
        # ufw (Ubuntu/Debian)
        log_info "检测到 ufw"
        ufw allow ${RABBITMQ_PORT}/tcp
        ufw allow ${RABBITMQ_MANAGEMENT_PORT}/tcp
        log_info "ufw 端口 ${RABBITMQ_PORT} 和 ${RABBITMQ_MANAGEMENT_PORT} 已开放"
    elif command -v iptables &> /dev/null; then
        # iptables (通用)
        log_info "检测到 iptables"
        iptables -I INPUT -p tcp --dport ${RABBITMQ_PORT} -j ACCEPT
        iptables -I INPUT -p tcp --dport ${RABBITMQ_MANAGEMENT_PORT} -j ACCEPT
        # 保存 iptables 规则
        if command -v iptables-save &> /dev/null; then
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || \
            iptables-save > /etc/sysconfig/iptables 2>/dev/null || true
        fi
        log_info "iptables 端口 ${RABBITMQ_PORT} 和 ${RABBITMQ_MANAGEMENT_PORT} 已开放"
    else
        log_info "未检测到防火墙或防火墙未启用"
    fi
}

# Ubuntu/Debian 安装
install_rabbitmq_ubuntu() {
    log_info "在 Ubuntu/Debian 上安装 RabbitMQ..."
    
    # 安装依赖
    apt-get update
    apt-get install -y curl gnupg apt-transport-https
    
    # 添加 RabbitMQ 仓库
    curl -1sLf "https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA" | gpg --dearmor | tee /usr/share/keyrings/com.rabbitmq.team.gpg > /dev/null
    curl -1sLf "https://github.com/rabbitmq/signing-keys/releases/download/3.0/cloudsmith.rabbitmq-erlang.E495BB49CC4BBE5B.key" | gpg --dearmor | tee /usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg > /dev/null
    curl -1sLf "https://github.com/rabbitmq/signing-keys/releases/download/3.0/cloudsmith.rabbitmq-server.9F4587F226208342.key" | gpg --dearmor | tee /usr/share/keyrings/rabbitmq.9F4587F226208342.gpg > /dev/null
    
    # 添加 apt 源
    tee /etc/apt/sources.list.d/rabbitmq.list <<EOF
deb [signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa1.novemberain.com/rabbitmq/rabbitmq-erlang/deb/ubuntu $(lsb_release -cs) main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.E495BB49CC4BBE5B.gpg] https://ppa1.novemberain.com/rabbitmq/rabbitmq-erlang/deb/ubuntu $(lsb_release -cs) main
deb [signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa1.novemberain.com/rabbitmq/rabbitmq-server/deb/ubuntu $(lsb_release -cs) main
deb-src [signed-by=/usr/share/keyrings/rabbitmq.9F4587F226208342.gpg] https://ppa1.novemberain.com/rabbitmq/rabbitmq-server/deb/ubuntu $(lsb_release -cs) main
EOF
    
    # 安装 Erlang 和 RabbitMQ
    apt-get update
    apt-get install -y erlang-base \
                       erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
                       erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
                       erlang-runtime-tools erlang-snmp erlang-ssl \
                       erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl
    
    apt-get install -y rabbitmq-server
    
    # 启动服务
    systemctl start rabbitmq-server
    systemctl enable rabbitmq-server
    
    log_info "RabbitMQ 安装完成"
}

# CentOS/RHEL 安装
install_rabbitmq_centos() {
    log_info "在 CentOS/RHEL 上安装 RabbitMQ..."
    
    # 安装 EPEL 仓库
    yum install -y epel-release
    
    # 安装 Erlang
    curl -s https://packagecloud.io/install/repositories/rabbitmq/erlang/script.rpm.sh | bash
    yum install -y erlang
    
    # 安装 RabbitMQ
    curl -s https://packagecloud.io/install/repositories/rabbitmq/rabbitmq-server/script.rpm.sh | bash
    yum install -y rabbitmq-server
    
    # 启动服务
    systemctl start rabbitmq-server
    systemctl enable rabbitmq-server
    
    log_info "RabbitMQ 安装完成"
}

# macOS 安装
install_rabbitmq_macos() {
    log_info "在 macOS 上安装 RabbitMQ..."
    
    if ! command -v brew &> /dev/null; then
        log_error "请先安装 Homebrew"
        exit 1
    fi
    
    brew install rabbitmq
    
    # 启动服务
    brew services start rabbitmq
    
    # 添加到 PATH
    export PATH="/usr/local/opt/rabbitmq/sbin:$PATH"
    
    log_info "RabbitMQ 安装完成"
}

# 配置 RabbitMQ
configure_rabbitmq() {
    log_info "配置 RabbitMQ..."
    
    # 启用管理插件
    rabbitmq-plugins enable rabbitmq_management
    
    # 等待服务启动
    sleep 5
    
    # 创建管理员用户
    rabbitmqctl add_user ${RABBITMQ_USER} ${RABBITMQ_PASSWORD} || true
    rabbitmqctl set_user_tags ${RABBITMQ_USER} administrator
    rabbitmqctl set_permissions -p ${RABBITMQ_VHOST} ${RABBITMQ_USER} ".*" ".*" ".*"
    
    # 删除默认 guest 用户（安全考虑）
    rabbitmqctl delete_user guest || true
    
    # 创建配置文件
    if [[ "$OS_TYPE" == "macos" ]]; then
        RABBITMQ_CONF_DIR="/usr/local/etc/rabbitmq"
    else
        RABBITMQ_CONF_DIR="/etc/rabbitmq"
    fi
    
    mkdir -p "$RABBITMQ_CONF_DIR"
    
    cat > "$RABBITMQ_CONF_DIR/rabbitmq.conf" <<EOF
# RabbitMQ 配置文件

# 网络设置
listeners.tcp.default = ${RABBITMQ_PORT}
management.tcp.port = ${RABBITMQ_MANAGEMENT_PORT}

# 日志设置
log.file.level = info
log.console = true
log.console.level = info

# 内存设置
vm_memory_high_watermark.relative = 0.6

# 磁盘空间设置
disk_free_limit.absolute = 2GB

# 心跳设置
heartbeat = 60

# 默认用户设置
default_vhost = ${RABBITMQ_VHOST}
default_user = ${RABBITMQ_USER}
default_pass = ${RABBITMQ_PASSWORD}
default_permissions.configure = .*
default_permissions.read = .*
default_permissions.write = .*
EOF
    
    # 重启 RabbitMQ
    if [[ "$OS_TYPE" == "macos" ]]; then
        brew services restart rabbitmq
    else
        systemctl restart rabbitmq-server
    fi
    
    log_info "RabbitMQ 配置完成"
}

# 创建测试队列
create_test_queue() {
    log_info "创建测试队列..."
    
    sleep 5
    
    # 使用 rabbitmqadmin 创建测试队列
    if command -v rabbitmqadmin &> /dev/null; then
        rabbitmqadmin -u ${RABBITMQ_USER} -p ${RABBITMQ_PASSWORD} declare queue name=test_queue durable=true
        rabbitmqadmin -u ${RABBITMQ_USER} -p ${RABBITMQ_PASSWORD} declare exchange name=test_exchange type=direct
        rabbitmqadmin -u ${RABBITMQ_USER} -p ${RABBITMQ_PASSWORD} declare binding source=test_exchange destination=test_queue routing_key=test
    fi
    
    log_info "测试队列创建完成"
}

# 测试 RabbitMQ
test_rabbitmq() {
    log_info "测试 RabbitMQ 连接..."
    
    if rabbitmqctl status > /dev/null 2>&1; then
        log_info "RabbitMQ 连接测试成功"
    else
        log_error "RabbitMQ 连接测试失败"
        exit 1
    fi
}

# 显示连接信息
show_connection_info() {
    echo ""
    echo "=========================================="
    echo "RabbitMQ 安装信息"
    echo "=========================================="
    echo "AMQP 端口: ${RABBITMQ_PORT}"
    echo "管理界面端口: ${RABBITMQ_MANAGEMENT_PORT}"
    echo "管理员用户: ${RABBITMQ_USER}"
    echo "管理员密码: ${RABBITMQ_PASSWORD}"
    echo "虚拟主机: ${RABBITMQ_VHOST}"
    echo ""
    echo "访问地址:"
    echo "  管理界面: http://localhost:${RABBITMQ_MANAGEMENT_PORT}"
    echo "  AMQP: amqp://localhost:${RABBITMQ_PORT}"
    echo ""
    echo "管理命令:"
    echo "  查看状态: rabbitmqctl status"
    echo "  查看队列: rabbitmqctl list_queues"
    echo "  查看用户: rabbitmqctl list_users"
    echo ""
    echo "Python 连接示例 (pika):"
    echo "  import pika"
    echo "  credentials = pika.PlainCredentials('${RABBITMQ_USER}', '${RABBITMQ_PASSWORD}')"
    echo "  connection = pika.BlockingConnection("
    echo "      pika.ConnectionParameters('localhost', ${RABBITMQ_PORT}, '${RABBITMQ_VHOST}', credentials)"
    echo "  )"
    echo ""
    echo "Python 连接示例 (aio-pika):"
    echo "  import aio_pika"
    echo "  connection = await aio_pika.connect_robust("
    echo "      'amqp://${RABBITMQ_USER}:${RABBITMQ_PASSWORD}@localhost:${RABBITMQ_PORT}/${RABBITMQ_VHOST}'"
    echo "  )"
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始安装 RabbitMQ..."
    
    # 检测操作系统并安装
    if [ "$OS_TYPE" == "ubuntu" ]; then
        install_rabbitmq_ubuntu
    elif [ "$OS_TYPE" == "centos" ]; then
        install_rabbitmq_centos
    elif [ "$OS_TYPE" == "macos" ]; then
        install_rabbitmq_macos
    else
        log_error "不支持的操作系统"
        exit 1
    fi
    
    # 配置 RabbitMQ
    configure_rabbitmq
    
    # 创建测试队列
    create_test_queue
    
    # 测试连接
    test_rabbitmq
    
    # 配置防火墙
    configure_firewall
    
    # 显示连接信息
    show_connection_info
    
    log_info "RabbitMQ 安装配置完成！"
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
