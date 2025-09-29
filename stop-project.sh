#!/bin/bash

# Vue FastAPI Admin - 项目停止脚本
# Copyright (c) 2025 左岚. All rights reserved.

echo "🛑 停止 Vue FastAPI Admin 项目服务..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 停止前端服务
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${BLUE}🔄 停止前端服务 (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID
        sleep 2
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  强制停止前端服务...${NC}"
            kill -9 $FRONTEND_PID
        fi
        echo -e "${GREEN}✅ 前端服务已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  前端服务进程不存在${NC}"
    fi
    rm -f frontend.pid
else
    echo -e "${YELLOW}⚠️  未找到前端服务PID文件${NC}"
fi

# 停止后端服务
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${BLUE}🔄 停止后端服务 (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID
        sleep 2
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  强制停止后端服务...${NC}"
            kill -9 $BACKEND_PID
        fi
        echo -e "${GREEN}✅ 后端服务已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  后端服务进程不存在${NC}"
    fi
    rm -f backend.pid
else
    echo -e "${YELLOW}⚠️  未找到后端服务PID文件${NC}"
fi

# 额外清理：通过端口杀死可能残留的进程
echo -e "${BLUE}🧹 清理残留进程...${NC}"

# 清理3000端口的进程
FRONTEND_PROCESSES=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$FRONTEND_PROCESSES" ]; then
    echo -e "${YELLOW}⚠️  发现3000端口残留进程，正在清理...${NC}"
    echo $FRONTEND_PROCESSES | xargs kill -9 2>/dev/null || true
fi

# 清理8000端口的进程
BACKEND_PROCESSES=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$BACKEND_PROCESSES" ]; then
    echo -e "${YELLOW}⚠️  发现8000端口残留进程，正在清理...${NC}"
    echo $BACKEND_PROCESSES | xargs kill -9 2>/dev/null || true
fi

# 清理可能的Node.js和Python进程
pkill -f "vite.*dev" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true

echo ""
echo -e "${GREEN}🎉 所有服务已停止！${NC}"
echo ""
echo -e "${BLUE}📋 清理完成：${NC}"
echo -e "  ✅ 前端服务 (端口3000) 已停止"
echo -e "  ✅ 后端服务 (端口8000) 已停止"
echo -e "  ✅ 进程文件已清理"
echo ""
echo -e "${BLUE}📝 日志文件保留：${NC}"
echo -e "  📄 frontend.log - 前端日志"
echo -e "  📄 backend.log - 后端日志"
echo ""
echo -e "${YELLOW}💡 提示: 如需重新启动，请运行 ./start-full-project.sh${NC}"
