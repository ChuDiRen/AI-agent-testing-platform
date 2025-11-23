#!/bin/bash

# =============================================================================
# Docker 安装脚本
# 自动检测操作系统并安装 Docker 和 Docker Compose
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[Docker]${NC} $1"
}

log_error() {
    echo -e "${RED}[Docker ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查 Docker 是否已安装
check_docker() {
    if command -v docker &> /dev/null; then
        log_info "Docker 已安装: $(docker --version)"
        return 0
    else
        return 1
    fi
}

# Ubuntu/Debian 安装 Docker
install_docker_ubuntu() {
    log_step "在 Ubuntu/Debian 上安装 Docker..."
    
    # 卸载旧版本
    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # 安装依赖
    apt-get update
    apt-get install -y ca-certificates curl gnupg lsb-release
    
    # 添加 Docker 官方 GPG 密钥（使用阿里云镜像）
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # 设置 Docker 仓库（使用阿里云镜像）
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 安装 Docker Engine
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    log_info "Docker 安装完成"
}

# CentOS/RHEL 安装 Docker
install_docker_centos() {
    log_step "在 CentOS/RHEL 上安装 Docker..."
    
    # 卸载旧版本
    yum remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine
    
    # 安装依赖
    yum install -y yum-utils
    
    # 添加 Docker 仓库（使用阿里云镜像）
    yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
    
    # 安装 Docker Engine
    yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    log_info "Docker 安装完成"
}

# 配置 Docker 镜像加速
configure_docker_mirror() {
    log_step "配置 Docker 镜像加速..."
    
    mkdir -p /etc/docker
    
    cat > /etc/docker/daemon.json <<EOF
{
  "registry-mirrors": [
    "https://docker.xuanyuan.me",
    "https://hub.rat.dev",
    "https://docker.m.daocloud.io",
    "https://doublezonline.cloud",
    "https://dislabaiot.xyz",
    "https://docker.mirrors.ustc.edu.cn",
    "https://docker.nju.edu.cn"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5
}
EOF
    
    log_info "Docker 镜像加速配置完成"
}

# 启动 Docker 服务
start_docker() {
    log_step "启动 Docker 服务..."
    
    systemctl daemon-reload
    systemctl enable docker
    
    # 启动 Docker 服务并捕获错误
    if ! systemctl start docker; then
        log_error "Docker 服务启动命令执行失败"
        log_error "详细错误信息："
        systemctl status docker --no-pager || true
        echo ""
        log_error "最近的日志："
        journalctl -xeu docker.service --no-pager -n 50 || true
        exit 1
    fi
    
    # 等待 Docker 服务完全就绪（最多30秒）
    log_step "等待 Docker 服务就绪..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if systemctl is-active --quiet docker && docker info > /dev/null 2>&1; then
            log_info "Docker 服务已就绪"
            break
        fi
        
        attempt=$((attempt + 1))
        if [ $attempt -eq $max_attempts ]; then
            log_error "Docker 服务启动超时（30秒）"
            log_error "当前服务状态："
            systemctl status docker --no-pager || true
            echo ""
            log_error "Docker 信息："
            docker info || true
            echo ""
            log_error "最近的日志："
            journalctl -xeu docker.service --no-pager -n 50 || true
            exit 1
        fi
        
        sleep 1
    done
    
    # 验证 Docker 是否正常运行
    log_step "验证 Docker 功能..."
    if docker run --rm hello-world > /dev/null 2>&1; then
        log_info "Docker 服务运行正常"
    else
        log_error "Docker 功能验证失败"
        log_error "服务状态："
        systemctl status docker --no-pager || true
        echo ""
        log_error "Docker 信息："
        docker info || true
        echo ""
        log_error "网络连接测试："
        docker run --rm hello-world || true
        exit 1
    fi
}

# 主函数
main() {
    log_info "开始安装 Docker..."
    
    # 检查是否已安装
    if check_docker; then
        log_info "Docker 已存在，跳过安装"
        configure_docker_mirror
        
        log_step "重启 Docker 服务以应用配置..."
        if ! systemctl restart docker; then
            log_error "Docker 服务重启失败"
            systemctl status docker --no-pager || true
            exit 1
        fi
        
        # 等待服务就绪
        log_step "等待 Docker 服务就绪..."
        local max_attempts=30
        local attempt=0
        
        while [ $attempt -lt $max_attempts ]; do
            if systemctl is-active --quiet docker && docker info > /dev/null 2>&1; then
                log_info "Docker 服务已就绪"
                return 0
            fi
            attempt=$((attempt + 1))
            [ $attempt -eq $max_attempts ] && log_error "Docker 服务重启超时" && exit 1
            sleep 1
        done
    fi
    
    # 检测操作系统
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_ID=$ID
    else
        log_error "无法检测操作系统"
        exit 1
    fi
    
    # 根据系统安装 Docker
    if [[ "$OS_ID" == "ubuntu" ]] || [[ "$OS_ID" == "debian" ]]; then
        install_docker_ubuntu
    elif [[ "$OS_ID" == "centos" ]] || [[ "$OS_ID" == "rhel" ]]; then
        install_docker_centos
    else
        log_error "不支持的操作系统: $OS_ID"
        exit 1
    fi
    
    # 配置镜像加速
    configure_docker_mirror
    
    # 启动 Docker
    start_docker
    
    log_info "Docker 安装完成！"
    docker --version
    docker compose version
}

# 执行主函数
main "$@"
