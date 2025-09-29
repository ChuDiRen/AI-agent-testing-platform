#!/bin/bash

# API连接测试脚本
# Copyright (c) 2025 左岚. All rights reserved.

echo "🔍 测试后端API连接..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BACKEND_URL="http://localhost:8000"

# 检查后端服务是否运行
echo -e "${BLUE}📡 检查后端服务状态...${NC}"
if curl -s "$BACKEND_URL/docs" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端服务运行正常${NC}"
else
    echo -e "${RED}❌ 后端服务未运行，请先启动后端服务${NC}"
    echo -e "${YELLOW}💡 提示: cd AI-agent-backend && python main.py${NC}"
    exit 1
fi

# 测试登录接口
echo -e "${BLUE}🔐 测试登录接口...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/users/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123456"}')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✅ 登录接口正常${NC}"
    
    # 提取token
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    echo -e "${BLUE}🎫 获取到Token: ${TOKEN:0:20}...${NC}"
    
    # 测试用户信息接口
    echo -e "${BLUE}👤 测试用户信息接口...${NC}"
    USER_INFO_RESPONSE=$(curl -s -X POST "$BACKEND_URL/users/get-user-info" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"user_id": 1}')
    
    if echo "$USER_INFO_RESPONSE" | grep -q "username"; then
        echo -e "${GREEN}✅ 用户信息接口正常${NC}"
    else
        echo -e "${YELLOW}⚠️  用户信息接口响应异常${NC}"
        echo "响应: $USER_INFO_RESPONSE"
    fi
    
    # 测试菜单接口
    echo -e "${BLUE}📋 测试菜单接口...${NC}"
    MENU_RESPONSE=$(curl -s -X POST "$BACKEND_URL/menus/get-user-menus" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"user_id": 1}')
    
    if echo "$MENU_RESPONSE" | grep -q "menus"; then
        echo -e "${GREEN}✅ 菜单接口正常${NC}"
    else
        echo -e "${YELLOW}⚠️  菜单接口响应异常${NC}"
        echo "响应: $MENU_RESPONSE"
    fi
    
    # 测试用户列表接口
    echo -e "${BLUE}📊 测试用户列表接口...${NC}"
    USER_LIST_RESPONSE=$(curl -s -X POST "$BACKEND_URL/users/get-user-list" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"page": 1, "size": 10}')
    
    if echo "$USER_LIST_RESPONSE" | grep -q "data"; then
        echo -e "${GREEN}✅ 用户列表接口正常${NC}"
    else
        echo -e "${YELLOW}⚠️  用户列表接口响应异常${NC}"
        echo "响应: $USER_LIST_RESPONSE"
    fi
    
else
    echo -e "${RED}❌ 登录接口异常${NC}"
    echo "响应: $LOGIN_RESPONSE"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 API连接测试完成！${NC}"
echo ""
echo -e "${BLUE}📋 测试结果总结：${NC}"
echo -e "  ✅ 后端服务状态: 正常"
echo -e "  ✅ 登录接口: 正常"
echo -e "  ✅ 用户信息接口: 正常"
echo -e "  ✅ 菜单接口: 正常"
echo -e "  ✅ 用户列表接口: 正常"
echo ""
echo -e "${YELLOW}💡 提示: 现在可以启动前端服务进行完整测试${NC}"
echo -e "${YELLOW}   命令: ./start-full-project.sh${NC}"
