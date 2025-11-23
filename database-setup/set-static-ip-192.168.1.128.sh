#!/bin/bash

# =============================================================================
# 静态IP配置脚本
# 将网络接口配置为固定IP: 192.168.1.128
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 网络配置参数
STATIC_IP="192.168.1.128"
NETMASK="255.255.255.0"
PREFIX="24"
GATEWAY="192.168.1.1"
DNS1="8.8.8.8"
DNS2="114.114.114.114"

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

# 检查root权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要 root 权限运行"
        log_info "请使用: sudo $0"
        exit 1
    fi
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
    else
        OS_TYPE="unknown"
    fi
    
    log_info "检测到操作系统: $OS_TYPE"
}

# 检测网络接口
detect_network_interface() {
    log_step "检测网络接口..."
    
    # 获取活动的网络接口（排除lo）
    INTERFACE=$(ip -o link show | awk -F': ' '{print $2}' | grep -v '^lo$' | head -n 1)
    
    if [ -z "$INTERFACE" ]; then
        log_error "未检测到可用的网络接口"
        exit 1
    fi
    
    log_info "检测到网络接口: $INTERFACE"
    
    # 显示当前IP
    CURRENT_IP=$(ip addr show $INTERFACE | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
    if [ -n "$CURRENT_IP" ]; then
        log_info "当前IP地址: $CURRENT_IP"
    fi
}

# 备份网络配置
backup_network_config() {
    log_step "备份当前网络配置..."
    
    BACKUP_DIR="/root/network-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    if [ "$OS_TYPE" == "ubuntu" ]; then
        # 备份 netplan 配置
        if [ -d /etc/netplan ]; then
            cp -r /etc/netplan "$BACKUP_DIR/" 2>/dev/null || true
        fi
        # 备份 interfaces 配置
        if [ -f /etc/network/interfaces ]; then
            cp /etc/network/interfaces "$BACKUP_DIR/" 2>/dev/null || true
        fi
    elif [ "$OS_TYPE" == "centos" ]; then
        # 备份网络脚本
        if [ -d /etc/sysconfig/network-scripts ]; then
            cp /etc/sysconfig/network-scripts/ifcfg-* "$BACKUP_DIR/" 2>/dev/null || true
        fi
        # 备份 NetworkManager 配置
        if [ -d /etc/NetworkManager/system-connections ]; then
            cp -r /etc/NetworkManager/system-connections "$BACKUP_DIR/" 2>/dev/null || true
        fi
    fi
    
    log_info "配置已备份到: $BACKUP_DIR"
}

# Ubuntu/Debian 配置静态IP (使用 netplan)
configure_ubuntu_netplan() {
    log_step "配置 Ubuntu/Debian 静态IP (netplan)..."
    
    # 查找 netplan 配置文件
    NETPLAN_FILE=$(ls /etc/netplan/*.yaml 2>/dev/null | head -n 1)
    
    if [ -z "$NETPLAN_FILE" ]; then
        NETPLAN_FILE="/etc/netplan/01-netcfg.yaml"
    fi
    
    # 创建新的 netplan 配置
    cat > "$NETPLAN_FILE" <<EOF
network:
  version: 2
  renderer: networkd
  ethernets:
    ${INTERFACE}:
      dhcp4: no
      addresses:
        - ${STATIC_IP}/${PREFIX}
      gateway4: ${GATEWAY}
      nameservers:
        addresses:
          - ${DNS1}
          - ${DNS2}
EOF
    
    log_info "netplan 配置文件已创建: $NETPLAN_FILE"
    
    # 应用配置
    log_step "应用 netplan 配置..."
    netplan apply
    
    log_info "netplan 配置已应用"
}

# Ubuntu/Debian 配置静态IP (使用 interfaces)
configure_ubuntu_interfaces() {
    log_step "配置 Ubuntu/Debian 静态IP (interfaces)..."
    
    # 创建 interfaces 配置
    cat > /etc/network/interfaces <<EOF
# This file describes the network interfaces available on your system
# and how to activate them. For more information, see interfaces(5).

source /etc/network/interfaces.d/*

# The loopback network interface
auto lo
iface lo inet loopback

# The primary network interface
auto ${INTERFACE}
iface ${INTERFACE} inet static
    address ${STATIC_IP}
    netmask ${NETMASK}
    gateway ${GATEWAY}
    dns-nameservers ${DNS1} ${DNS2}
EOF
    
    log_info "interfaces 配置文件已创建"
    
    # 重启网络服务
    log_step "重启网络服务..."
    systemctl restart networking || service networking restart
    
    log_info "网络服务已重启"
}

# CentOS/RHEL 配置静态IP (使用 nmcli)
configure_centos_nmcli() {
    log_step "配置 CentOS/RHEL 静态IP (nmcli)..."
    
    # 获取连接名称
    CONNECTION=$(nmcli -t -f NAME,DEVICE connection show --active | grep "$INTERFACE" | cut -d':' -f1)
    
    if [ -z "$CONNECTION" ]; then
        CONNECTION="$INTERFACE"
    fi
    
    log_info "配置连接: $CONNECTION"
    
    # 配置静态IP
    nmcli connection modify "$CONNECTION" ipv4.method manual
    nmcli connection modify "$CONNECTION" ipv4.addresses "${STATIC_IP}/${PREFIX}"
    nmcli connection modify "$CONNECTION" ipv4.gateway "${GATEWAY}"
    nmcli connection modify "$CONNECTION" ipv4.dns "${DNS1} ${DNS2}"
    nmcli connection modify "$CONNECTION" connection.autoconnect yes
    
    # 重启连接
    log_step "重启网络连接..."
    nmcli connection down "$CONNECTION" && nmcli connection up "$CONNECTION"
    
    log_info "网络连接已重启"
}

# CentOS/RHEL 配置静态IP (使用 network-scripts)
configure_centos_scripts() {
    log_step "配置 CentOS/RHEL 静态IP (network-scripts)..."
    
    IFCFG_FILE="/etc/sysconfig/network-scripts/ifcfg-${INTERFACE}"
    
    # 创建网络配置文件
    cat > "$IFCFG_FILE" <<EOF
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=no
NAME=${INTERFACE}
DEVICE=${INTERFACE}
ONBOOT=yes
IPADDR=${STATIC_IP}
NETMASK=${NETMASK}
GATEWAY=${GATEWAY}
DNS1=${DNS1}
DNS2=${DNS2}
EOF
    
    log_info "网络配置文件已创建: $IFCFG_FILE"
    
    # 重启网络服务
    log_step "重启网络服务..."
    systemctl restart network || service network restart
    
    log_info "网络服务已重启"
}

# 配置DNS
configure_dns() {
    log_step "配置 DNS 服务器..."
    
    # 配置 resolv.conf
    cat > /etc/resolv.conf <<EOF
# Generated by set-static-ip script
nameserver ${DNS1}
nameserver ${DNS2}
EOF
    
    # 防止 resolv.conf 被覆盖
    chattr +i /etc/resolv.conf 2>/dev/null || true
    
    log_info "DNS 配置完成"
}

# 验证网络配置
verify_network() {
    log_step "验证网络配置..."
    
    sleep 3
    
    # 检查IP地址
    NEW_IP=$(ip addr show $INTERFACE | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
    
    if [ "$NEW_IP" == "$STATIC_IP" ]; then
        log_info "✓ IP地址配置成功: $NEW_IP"
    else
        log_warn "IP地址可能未正确配置，当前IP: $NEW_IP"
    fi
    
    # 测试网关连通性
    if ping -c 2 -W 3 $GATEWAY > /dev/null 2>&1; then
        log_info "✓ 网关连通性测试成功: $GATEWAY"
    else
        log_warn "无法ping通网关: $GATEWAY"
    fi
    
    # 测试DNS解析
    if ping -c 2 -W 3 www.baidu.com > /dev/null 2>&1; then
        log_info "✓ DNS解析测试成功"
    else
        log_warn "DNS解析可能存在问题"
    fi
}

# 显示配置信息
show_config_info() {
    echo ""
    echo "=========================================="
    echo "  静态IP配置完成"
    echo "=========================================="
    echo "网络接口: $INTERFACE"
    echo "IP地址: $STATIC_IP"
    echo "子网掩码: $NETMASK ($PREFIX)"
    echo "网关: $GATEWAY"
    echo "DNS1: $DNS1"
    echo "DNS2: $DNS2"
    echo ""
    echo "配置备份: $BACKUP_DIR"
    echo ""
    echo "验证命令:"
    echo "  ip addr show $INTERFACE"
    echo "  ip route show"
    echo "  cat /etc/resolv.conf"
    echo "=========================================="
}

# 主函数
main() {
    echo "=========================================="
    echo "  静态IP配置脚本"
    echo "  目标IP: $STATIC_IP"
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
    
    # 检测网络接口
    detect_network_interface
    
    # 显示配置信息
    log_warn "即将配置静态IP: $STATIC_IP"
    log_warn "网络接口: $INTERFACE"
    log_info "自动执行配置，无需确认"
    
    # 备份配置
    backup_network_config
    
    # 根据操作系统配置网络
    if [ "$OS_TYPE" == "ubuntu" ]; then
        if command -v netplan &> /dev/null; then
            configure_ubuntu_netplan
        else
            configure_ubuntu_interfaces
        fi
    elif [ "$OS_TYPE" == "centos" ]; then
        if command -v nmcli &> /dev/null; then
            configure_centos_nmcli
        else
            configure_centos_scripts
        fi
    fi
    
    # 配置DNS
    configure_dns
    
    # 验证配置
    verify_network
    
    # 显示配置信息
    show_config_info
    
    log_info "静态IP配置完成！"
    log_warn "如果SSH连接断开，请使用新IP: $STATIC_IP 重新连接"
}

main "$@"
