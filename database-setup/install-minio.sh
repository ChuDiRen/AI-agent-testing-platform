#!/bin/bash

# =============================================================================
# MinIO 安装脚本
# 自动检测操作系统并安装配置 MinIO 对象存储
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置变量
MINIO_VERSION="latest"
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_ROOT_USER="admin"
MINIO_ROOT_PASSWORD="admin123456"
MINIO_DATA_DIR="${DATA_DIR:-/var/lib/minio/data}"
MINIO_CONFIG_DIR="${DATA_DIR:-/etc/minio}"

log_info() {
    echo -e "${GREEN}[MinIO]${NC} $1"
}

log_error() {
    echo -e "${RED}[MinIO ERROR]${NC} $1"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙，开放端口 ${MINIO_API_PORT} 和 ${MINIO_CONSOLE_PORT}..."
    
    # 检测防火墙类型并配置
    if command -v firewall-cmd &> /dev/null; then
        # firewalld (CentOS/RHEL/Fedora)
        log_info "检测到 firewalld"
        firewall-cmd --permanent --add-port=${MINIO_API_PORT}/tcp
        firewall-cmd --permanent --add-port=${MINIO_CONSOLE_PORT}/tcp
        firewall-cmd --reload
        log_info "firewalld 端口 ${MINIO_API_PORT} 和 ${MINIO_CONSOLE_PORT} 已开放"
    elif command -v ufw &> /dev/null; then
        # ufw (Ubuntu/Debian)
        log_info "检测到 ufw"
        ufw allow ${MINIO_API_PORT}/tcp
        ufw allow ${MINIO_CONSOLE_PORT}/tcp
        log_info "ufw 端口 ${MINIO_API_PORT} 和 ${MINIO_CONSOLE_PORT} 已开放"
    elif command -v iptables &> /dev/null; then
        # iptables (通用)
        log_info "检测到 iptables"
        iptables -I INPUT -p tcp --dport ${MINIO_API_PORT} -j ACCEPT
        iptables -I INPUT -p tcp --dport ${MINIO_CONSOLE_PORT} -j ACCEPT
        # 保存 iptables 规则
        if command -v iptables-save &> /dev/null; then
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || \
            iptables-save > /etc/sysconfig/iptables 2>/dev/null || true
        fi
        log_info "iptables 端口 ${MINIO_API_PORT} 和 ${MINIO_CONSOLE_PORT} 已开放"
    else
        log_info "未检测到防火墙或防火墙未启用"
    fi
}

# Ubuntu/Debian 安装
install_minio_ubuntu() {
    log_info "在 Ubuntu/Debian 上安装 MinIO..."
    
    # 下载 MinIO 二进制文件
    wget https://dl.min.io/server/minio/release/linux-amd64/minio -O /usr/local/bin/minio
    chmod +x /usr/local/bin/minio
    
    # 下载 MinIO Client
    wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc
    chmod +x /usr/local/bin/mc
    
    log_info "MinIO 二进制文件下载完成"
}

# CentOS/RHEL 安装
install_minio_centos() {
    log_info "在 CentOS/RHEL 上安装 MinIO..."
    
    # 下载 MinIO 二进制文件
    wget https://dl.min.io/server/minio/release/linux-amd64/minio -O /usr/local/bin/minio
    chmod +x /usr/local/bin/minio
    
    # 下载 MinIO Client
    wget https://dl.min.io/client/mc/release/linux-amd64/mc -O /usr/local/bin/mc
    chmod +x /usr/local/bin/mc
    
    log_info "MinIO 二进制文件下载完成"
}

# macOS 安装
install_minio_macos() {
    log_info "在 macOS 上安装 MinIO..."
    
    if ! command -v brew &> /dev/null; then
        log_error "请先安装 Homebrew"
        exit 1
    fi
    
    brew install minio/stable/minio
    brew install minio/stable/mc
    
    log_info "MinIO 安装完成"
}

# 配置 MinIO
configure_minio() {
    log_info "配置 MinIO..."
    
    # 创建必要的目录
    mkdir -p "$MINIO_DATA_DIR"
    mkdir -p "$MINIO_CONFIG_DIR"
    
    # 创建 MinIO 用户（仅 Linux）
    if [[ "$OS_TYPE" != "macos" ]]; then
        if ! id "minio" &>/dev/null; then
            useradd -r -s /sbin/nologin minio
        fi
        chown -R minio:minio "$MINIO_DATA_DIR"
        chown -R minio:minio "$MINIO_CONFIG_DIR"
    fi
    
    # 创建环境变量配置文件
    cat > "$MINIO_CONFIG_DIR/minio.env" <<EOF
# MinIO 环境变量配置
MINIO_ROOT_USER=${MINIO_ROOT_USER}
MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
MINIO_VOLUMES=${MINIO_DATA_DIR}
MINIO_OPTS="--address :${MINIO_API_PORT} --console-address :${MINIO_CONSOLE_PORT}"
EOF
    
    # 创建 systemd 服务文件（仅 Linux）
    if [[ "$OS_TYPE" != "macos" ]]; then
        cat > /etc/systemd/system/minio.service <<EOF
[Unit]
Description=MinIO Object Storage
Documentation=https://docs.min.io
Wants=network-online.target
After=network-online.target
AssertFileIsExecutable=/usr/local/bin/minio

[Service]
WorkingDirectory=/usr/local

User=minio
Group=minio

EnvironmentFile=${MINIO_CONFIG_DIR}/minio.env
ExecStart=/usr/local/bin/minio server \$MINIO_OPTS \$MINIO_VOLUMES

# Let systemd restart this service always
Restart=always

# Specifies the maximum file descriptor number that can be opened by this process
LimitNOFILE=65536

# Specifies the maximum number of threads this process can create
TasksMax=infinity

# Disable timeout logic and wait until process is stopped
TimeoutStopSec=infinity
SendSIGKILL=no

[Install]
WantedBy=multi-user.target
EOF
        
        # 重新加载 systemd 并启动服务
        systemctl daemon-reload
        systemctl enable minio
        systemctl start minio
    else
        # macOS 使用 launchd
        cat > ~/Library/LaunchAgents/io.min.minio.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>io.min.minio</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/minio</string>
        <string>server</string>
        <string>--address</string>
        <string>:${MINIO_API_PORT}</string>
        <string>--console-address</string>
        <string>:${MINIO_CONSOLE_PORT}</string>
        <string>${MINIO_DATA_DIR}</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>MINIO_ROOT_USER</key>
        <string>${MINIO_ROOT_USER}</string>
        <key>MINIO_ROOT_PASSWORD</key>
        <string>${MINIO_ROOT_PASSWORD}</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF
        launchctl load ~/Library/LaunchAgents/io.min.minio.plist
    fi
    
    log_info "MinIO 配置完成"
}

# 配置 MinIO Client
configure_mc() {
    log_info "配置 MinIO Client..."
    
    # 等待 MinIO 启动
    sleep 5
    
    # 配置 mc 别名
    mc alias set local http://localhost:${MINIO_API_PORT} ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}
    
    # 创建测试桶
    mc mb local/test-bucket --ignore-existing
    mc mb local/uploads --ignore-existing
    
    # 设置桶策略为公开读
    mc anonymous set download local/test-bucket
    
    log_info "MinIO Client 配置完成"
}

# 测试 MinIO
test_minio() {
    log_info "测试 MinIO 连接..."
    
    sleep 3
    
    if mc admin info local > /dev/null 2>&1; then
        log_info "MinIO 连接测试成功"
    else
        log_error "MinIO 连接测试失败"
        exit 1
    fi
}

# 显示连接信息
show_connection_info() {
    echo ""
    echo "=========================================="
    echo "MinIO 安装信息"
    echo "=========================================="
    echo "API 端口: ${MINIO_API_PORT}"
    echo "控制台端口: ${MINIO_CONSOLE_PORT}"
    echo "Root 用户: ${MINIO_ROOT_USER}"
    echo "Root 密码: ${MINIO_ROOT_PASSWORD}"
    echo "数据目录: ${MINIO_DATA_DIR}"
    echo ""
    echo "访问地址:"
    echo "  API: http://localhost:${MINIO_API_PORT}"
    echo "  控制台: http://localhost:${MINIO_CONSOLE_PORT}"
    echo ""
    echo "已创建的桶:"
    echo "  - test-bucket (公开读)"
    echo "  - uploads (私有)"
    echo ""
    echo "MinIO Client 命令:"
    echo "  mc ls local/"
    echo "  mc cp file.txt local/test-bucket/"
    echo ""
    echo "Python 连接示例:"
    echo "  from minio import Minio"
    echo "  client = Minio("
    echo "      'localhost:${MINIO_API_PORT}',"
    echo "      access_key='${MINIO_ROOT_USER}',"
    echo "      secret_key='${MINIO_ROOT_PASSWORD}',"
    echo "      secure=False"
    echo "  )"
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始安装 MinIO..."
    
    # 检测操作系统并安装
    if [ "$OS_TYPE" == "ubuntu" ]; then
        install_minio_ubuntu
    elif [ "$OS_TYPE" == "centos" ]; then
        install_minio_centos
    elif [ "$OS_TYPE" == "macos" ]; then
        install_minio_macos
    else
        log_error "不支持的操作系统"
        exit 1
    fi
    
    # 配置 MinIO
    configure_minio
    
    # 配置 MinIO Client
    configure_mc
    
    # 测试连接
    test_minio
    
    # 配置防火墙
    configure_firewall
    
    # 显示连接信息
    show_connection_info
    
    log_info "MinIO 安装配置完成！"
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
