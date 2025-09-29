#!/bin/bash

# Vue FastAPI Admin - 完整项目启动脚本
# Copyright (c) 2025 左岚. All rights reserved.

echo "🚀 启动 Vue FastAPI Admin 完整项目..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否在正确的目录
if [ ! -d "AI-agent-frontend-naive" ] || [ ! -d "AI-agent-backend" ]; then
    echo -e "${RED}❌ 错误: 请在项目根目录下运行此脚本${NC}"
    exit 1
fi

# 函数：检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # 端口被占用
    else
        return 1  # 端口空闲
    fi
}

# 函数：启动后端服务
start_backend() {
    echo -e "${BLUE}📦 启动后端服务...${NC}"
    
    # 检查后端端口
    if check_port 8000; then
        echo -e "${YELLOW}⚠️  端口8000已被占用，尝试停止现有服务...${NC}"
        pkill -f "python.*main.py" 2>/dev/null || true
        sleep 2
    fi
    
    cd AI-agent-backend
    
    # 检查Python环境
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ 错误: 未找到Python，请先安装Python 3.8+${NC}"
        exit 1
    fi
    
    # 检查依赖
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}❌ 错误: 未找到requirements.txt文件${NC}"
        exit 1
    fi
    
    # 安装依赖（如果需要）
    echo -e "${BLUE}📦 检查Python依赖...${NC}"
    pip install -r requirements.txt > /dev/null 2>&1
    
    # 启动后端服务
    echo -e "${GREEN}✅ 启动后端服务 (端口: 8000)${NC}"
    nohup python main.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    cd ..
    
    # 等待后端启动
    echo -e "${BLUE}⏳ 等待后端服务启动...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 后端服务启动成功！${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ 后端服务启动超时${NC}"
            exit 1
        fi
        sleep 1
    done
}

# 函数：启动前端服务
start_frontend() {
    echo -e "${BLUE}📦 启动前端服务...${NC}"
    
    # 检查前端端口
    if check_port 3000; then
        echo -e "${YELLOW}⚠️  端口3000已被占用，尝试停止现有服务...${NC}"
        pkill -f "vite.*dev" 2>/dev/null || true
        sleep 2
    fi
    
    cd AI-agent-frontend-naive
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ 错误: 未找到Node.js，请先安装Node.js 18+${NC}"
        exit 1
    fi
    
    # 检查pnpm
    if ! command -v pnpm &> /dev/null; then
        echo -e "${BLUE}📦 安装pnpm...${NC}"
        npm install -g pnpm
    fi
    
    # 检查依赖
    if [ ! -d "node_modules" ]; then
        echo -e "${BLUE}📦 安装前端依赖...${NC}"
        pnpm install
    fi
    
    # 启动前端服务
    echo -e "${GREEN}✅ 启动前端服务 (端口: 3000)${NC}"
    nohup pnpm dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    cd ..
    
    # 等待前端启动
    echo -e "${BLUE}⏳ 等待前端服务启动...${NC}"
    for i in {1..60}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 前端服务启动成功！${NC}"
            break
        fi
        if [ $i -eq 60 ]; then
            echo -e "${RED}❌ 前端服务启动超时${NC}"
            exit 1
        fi
        sleep 1
    done
}

# 函数：显示服务状态
show_status() {
    echo ""
    echo -e "${GREEN}🎉 所有服务启动完成！${NC}"
    echo ""
    echo -e "${BLUE}📋 服务信息：${NC}"
    echo -e "  前端服务: ${GREEN}http://localhost:3000${NC}"
    echo -e "  后端服务: ${GREEN}http://localhost:8000${NC}"
    echo -e "  API文档:  ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${BLUE}🔑 默认登录信息：${NC}"
    echo -e "  用户名: ${YELLOW}admin${NC}"
    echo -e "  密码:   ${YELLOW}123456${NC}"
    echo ""
    echo -e "${BLUE}📝 日志文件：${NC}"
    echo -e "  前端日志: ${YELLOW}frontend.log${NC}"
    echo -e "  后端日志: ${YELLOW}backend.log${NC}"
    echo ""
    echo -e "${BLUE}🛑 停止服务：${NC}"
    echo -e "  运行: ${YELLOW}./stop-project.sh${NC}"
    echo ""
}

# 主执行流程
main() {
    # 启动后端
    start_backend
    
    # 启动前端
    start_frontend
    
    # 显示状态
    show_status
    
    # 询问是否打开浏览器
    read -p "是否自动打开浏览器？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v xdg-open &> /dev/null; then
            xdg-open http://localhost:3000
        elif command -v open &> /dev/null; then
            open http://localhost:3000
        else
            echo -e "${YELLOW}⚠️  无法自动打开浏览器，请手动访问: http://localhost:3000${NC}"
        fi
    fi
    
    echo -e "${GREEN}✨ 项目启动完成！按 Ctrl+C 查看实时日志${NC}"
    
    # 实时显示日志
    trap 'echo -e "\n${YELLOW}📋 查看完整日志请运行: tail -f frontend.log backend.log${NC}"; exit 0' INT
    tail -f frontend.log backend.log 2>/dev/null || sleep infinity
}

# 执行主函数
main
