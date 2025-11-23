#!/bin/bash

# =============================================================================
# 环境准备脚本
# 功能：网络诊断 + 修复 + 镜像源配置
# 作者：左岚团队
# 版本：2.0
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# 网络配置参数（请根据实际环境修改）
# ============================================================================
GATEWAY="192.168.1.2"           # 默认网关地址
DNS1="114.114.114.114"          # 主 DNS（114 DNS）
DNS2="223.5.5.5"                # 备用 DNS（阿里云 DNS）
DNS3="119.29.29.29"             # 备用 DNS（腾讯 DNS）
DNS4="8.8.8.8"                  # 备用 DNS（Google DNS）

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_fail() {
    echo -e "${RED}[✗]${NC} $1"
}

# ============================================================================
# 检查 root 权限
# ============================================================================
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用 root 权限运行此脚本"
        echo "使用: sudo bash prepare-environment.sh"
        exit 1
    fi
}

# ============================================================================
# 第一部分：网络诊断和修复
# ============================================================================

check_network_interface() {
    log_step "检查网络接口..."
    
    local interfaces=$(ip -o link show | awk -F': ' '{print $2}' | grep -v lo)
    if [ -z "$interfaces" ]; then
        log_fail "未找到网络接口"
        return 1
    fi
    
    # 检查是否有 UP 状态的接口
    local up_count=$(ip link show | grep -c "state UP" || true)
    if [ "$up_count" -eq 0 ]; then
        log_warn "所有网络接口都处于 DOWN 状态，尝试启用..."
        for iface in $interfaces; do
            ip link set "$iface" up 2>/dev/null || true
        done
        sleep 2
    fi
    
    log_success "网络接口正常"
    return 0
}

fix_gateway() {
    log_step "配置网关..."
    
    # 获取主网络接口
    local interface=$(ip -o link show | awk -F': ' '{print $2}' | grep -v '^lo$' | head -n 1)
    
    if [ -z "$interface" ]; then
        log_error "未找到可用的网络接口"
        return 1
    fi
    
    log_info "网络接口: $interface"
    
    # 删除旧的默认路由
    ip route del default 2>/dev/null || true
    
    # 添加新的默认路由
    if ip route add default via $GATEWAY dev $interface 2>/dev/null; then
        log_success "网关配置成功: $GATEWAY"
    else
        log_warn "网关配置失败，可能已存在"
    fi
    
    # 测试网关连通性
    log_info "测试网关连通性..."
    if ping -c 2 -W 2 $GATEWAY > /dev/null 2>&1; then
        log_success "网关连接正常"
        return 0
    else
        log_fail "无法连接到网关 $GATEWAY"
        return 1
    fi
}

fix_dns() {
    log_step "配置 DNS 服务器..."
    
    # 备份原配置
    if [ -f /etc/resolv.conf ]; then
        cp /etc/resolv.conf /etc/resolv.conf.backup.$(date +%Y%m%d-%H%M%S) 2>/dev/null || true
    fi
    
    # 解除文件锁定（如果之前被锁定）
    chattr -i /etc/resolv.conf 2>/dev/null || true
    
    # 配置 DNS
    cat > /etc/resolv.conf <<EOF
# 自动生成的 DNS 配置
# 配置时间: $(date '+%Y-%m-%d %H:%M:%S')
# 备份文件: /etc/resolv.conf.backup.*

# 国内 DNS 服务器（优先）
nameserver $DNS1
nameserver $DNS2
nameserver $DNS3

# 国际 DNS 服务器（备用）
nameserver $DNS4
EOF
    
    # 防止被 NetworkManager 覆盖
    chattr +i /etc/resolv.conf 2>/dev/null || true
    
    log_success "DNS 配置完成"
    log_info "DNS: $DNS1, $DNS2, $DNS3, $DNS4"
}

test_network() {
    log_step "测试网络连通性..."
    
    local test_hosts=("www.baidu.com" "mirrors.aliyun.com")
    local success=0
    
    for host in "${test_hosts[@]}"; do
        if ping -c 2 -W 3 "$host" > /dev/null 2>&1; then
            log_success "$host 连接成功"
            success=1
            break
        fi
    done
    
    if [ "$success" -eq 1 ]; then
        log_success "网络连接正常"
        return 0
    else
        log_fail "网络连接失败"
        return 1
    fi
}

# ============================================================================
# 第二部分：镜像源配置
# ============================================================================

detect_os() {
    log_step "检测操作系统..."
    
    if [ ! -f /etc/os-release ]; then
        log_error "无法检测操作系统"
        return 1
    fi
    
    . /etc/os-release
    OS_ID=$ID
    OS_VERSION_CODENAME=$VERSION_CODENAME
    
    log_info "操作系统: $OS_ID $OS_VERSION_CODENAME"
    
    if [[ "$OS_ID" == "ubuntu" ]] || [[ "$OS_ID" == "debian" ]]; then
        return 0
    elif [[ "$OS_ID" == "centos" ]] || [[ "$OS_ID" == "rhel" ]]; then
        log_warn "CentOS/RHEL 系统暂不支持自动配置镜像源"
        return 1
    else
        log_warn "不支持的操作系统: $OS_ID"
        return 1
    fi
}

configure_apt_mirror() {
    log_step "配置 APT 镜像源..."
    
    # 备份原配置
    if [ -f /etc/apt/sources.list ]; then
        local backup_file="/etc/apt/sources.list.backup.$(date +%Y%m%d-%H%M%S)"
        cp /etc/apt/sources.list "$backup_file"
        log_info "已备份原配置: $backup_file"
    fi
    
    # 配置阿里云镜像
    log_info "使用阿里云镜像源..."
    cat > /etc/apt/sources.list <<EOF
# 阿里云镜像源 - $OS_VERSION_CODENAME
# 配置时间: $(date '+%Y-%m-%d %H:%M:%S')

deb http://mirrors.aliyun.com/$OS_ID/ $OS_VERSION_CODENAME main restricted universe multiverse
deb http://mirrors.aliyun.com/$OS_ID/ $OS_VERSION_CODENAME-security main restricted universe multiverse
deb http://mirrors.aliyun.com/$OS_ID/ $OS_VERSION_CODENAME-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/$OS_ID/ $OS_VERSION_CODENAME-backports main restricted universe multiverse

# 源码仓库（可选，默认禁用）
# deb-src http://mirrors.aliyun.com/$OS_ID/ $OS_VERSION_CODENAME main restricted universe multiverse
EOF
    
    log_success "镜像源配置完成"
}

update_apt_cache() {
    log_step "更新 APT 软件包缓存..."
    
    # 清理旧缓存
    apt-get clean
    
    # 更新缓存
    log_info "正在更新软件包列表，请稍候..."
    if apt-get update; then
        log_success "APT 缓存更新成功"
        return 0
    else
        log_error "APT 缓存更新失败"
        return 1
    fi
}

# ============================================================================
# 显示诊断报告
# ============================================================================

show_report() {
    echo ""
    echo "=========================================="
    echo "  环境配置报告"
    echo "=========================================="
    echo ""
    
    echo "【网络配置】"
    echo "  网关: $GATEWAY"
    echo "  DNS:  $DNS1, $DNS2, $DNS3, $DNS4"
    echo ""
    
    echo "【网络接口】"
    ip -o link show | grep -v lo | awk -F': ' '{print "  " $2}' | while read iface; do
        local status=$(ip link show "$iface" | grep -o "state [A-Z]*" | awk '{print $2}')
        echo "  $iface: $status"
    done
    echo ""
    
    echo "【IP 地址】"
    ip -4 addr show | grep inet | grep -v 127.0.0.1 | awk '{print "  " $2 " (" $NF ")"}' || echo "  未配置"
    echo ""
    
    echo "【路由表】"
    ip route show | while read line; do
        echo "  $line"
    done
    echo ""
    
    if [[ "$OS_ID" == "ubuntu" ]] || [[ "$OS_ID" == "debian" ]]; then
        echo "【镜像源】"
        echo "  阿里云镜像: http://mirrors.aliyun.com/$OS_ID/"
        echo ""
    fi
    
    echo "=========================================="
}

# ============================================================================
# 主函数
# ============================================================================

main() {
    echo ""
    echo "=========================================="
    echo "  环境准备脚本"
    echo "  网络诊断 + 镜像源配置"
    echo "=========================================="
    echo ""
    
    # 检查 root 权限
    check_root
    
    # 第一部分：网络诊断和修复
    echo ""
    log_step "第一部分：网络诊断和修复"
    echo ""
    
    local network_ok=1
    
    # 1. 检查网络接口
    if ! check_network_interface; then
        network_ok=0
    fi
    
    # 2. 配置网关
    if ! fix_gateway; then
        network_ok=0
    fi
    
    # 3. 配置 DNS
    fix_dns
    
    # 4. 测试网络
    if ! test_network; then
        network_ok=0
    fi
    
    if [ "$network_ok" -eq 0 ]; then
        echo ""
        log_error "网络配置失败，请检查："
        echo "  1. 虚拟机网络适配器是否启用"
        echo "  2. 网关地址是否正确（当前: $GATEWAY）"
        echo "  3. 宿主机网络是否正常"
        echo ""
        echo "如需修改网关地址，请编辑此脚本："
        echo "  nano prepare-environment.sh"
        echo "  找到: GATEWAY=\"192.168.1.0\""
        echo "  改为: GATEWAY=\"您的网关地址\""
        echo ""
        exit 1
    fi
    
    # 第二部分：镜像源配置
    echo ""
    log_step "第二部分：镜像源配置"
    echo ""
    
    if detect_os; then
        configure_apt_mirror
        
        if update_apt_cache; then
            log_success "镜像源配置成功"
        else
            log_error "镜像源配置失败"
            exit 1
        fi
    else
        log_warn "跳过镜像源配置"
    fi
    
    # 显示报告
    show_report
    
    # 完成
    echo ""
    log_success "环境准备完成！"
    echo ""
    echo "下一步："
    echo "  1. 安装 Docker:    sudo bash install-docker.sh"
    echo "  2. 部署所有服务:   sudo bash deploy-all.sh"
    echo ""
    echo "  或单独部署："
    echo "    sudo bash deploy-mysql.sh"
    echo "    sudo bash deploy-redis.sh"
    echo "    sudo bash deploy-postgres.sh"
    echo "    sudo bash deploy-minio.sh"
    echo "    sudo bash deploy-rabbitmq.sh"
    echo ""
}

# 显示使用帮助
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    cat <<EOF
环境准备脚本

功能:
    1. 网络诊断和修复
       - 检查网络接口
       - 配置网关（默认: 192.168.1.0）
       - 配置 DNS 服务器
       - 测试网络连通性
    
    2. 镜像源配置
       - 自动检测操作系统
       - 配置阿里云镜像源（Ubuntu/Debian）
       - 更新软件包缓存

使用方法:
    sudo bash prepare-environment.sh

修改网关地址:
    nano prepare-environment.sh
    找到: GATEWAY="192.168.1.0"
    改为: GATEWAY="您的网关地址"

注意事项:
    - 必须使用 root 权限运行
    - 会自动备份原有配置
    - DNS 配置会被锁定，防止被覆盖
EOF
    exit 0
fi

# 执行主函数
main "$@"
