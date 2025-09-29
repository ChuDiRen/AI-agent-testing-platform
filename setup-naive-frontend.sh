#!/bin/bash

# Vue FastAPI Admin - Naive UI版本安装脚本
# Copyright (c) 2025 左岚. All rights reserved.

echo "🚀 开始安装 Vue FastAPI Admin - Naive UI版本..."

# 检查Node.js版本
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到Node.js，请先安装Node.js 18+版本"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ 错误: Node.js版本过低，需要18+版本，当前版本: $(node -v)"
    exit 1
fi

echo "✅ Node.js版本检查通过: $(node -v)"

# 检查pnpm
if ! command -v pnpm &> /dev/null; then
    echo "📦 未找到pnpm，正在安装..."
    npm install -g pnpm
fi

echo "✅ pnpm版本: $(pnpm -v)"

# 进入前端目录
cd AI-agent-frontend-naive

echo "📦 正在安装依赖..."
pnpm install

if [ $? -eq 0 ]; then
    echo "✅ 依赖安装成功！"
else
    echo "❌ 依赖安装失败，请检查网络连接或手动执行 pnpm install"
    exit 1
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 可用命令："
echo "  pnpm dev      - 启动开发服务器"
echo "  pnpm build    - 构建生产版本"
echo "  pnpm preview  - 预览生产版本"
echo ""
echo "🌐 访问地址："
echo "  开发环境: http://localhost:3000"
echo "  后端API:  http://localhost:8000"
echo ""
echo "🔑 默认登录信息："
echo "  用户名: admin"
echo "  密码:   123456"
echo ""
echo "💡 提示: 请确保后端服务已启动在8000端口"
echo ""

# 询问是否立即启动开发服务器
read -p "是否立即启动开发服务器？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 正在启动开发服务器..."
    pnpm dev
fi
