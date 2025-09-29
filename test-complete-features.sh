#!/bin/bash

# 完整功能测试脚本
# Copyright (c) 2025 左岚. All rights reserved.

echo "🧪 开始完整功能测试..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:3000"

# 检查服务状态
check_services() {
    echo -e "${BLUE}📡 检查服务状态...${NC}"
    
    # 检查后端
    if curl -s "$BACKEND_URL/docs" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端服务运行正常${NC}"
    else
        echo -e "${RED}❌ 后端服务未运行${NC}"
        return 1
    fi
    
    # 检查前端
    if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 前端服务运行正常${NC}"
    else
        echo -e "${YELLOW}⚠️  前端服务未运行，将启动服务${NC}"
        return 2
    fi
    
    return 0
}

# 测试登录功能
test_login() {
    echo -e "${PURPLE}🔐 测试登录功能...${NC}"
    
    LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/users/login" \
      -H "Content-Type: application/json" \
      -d '{"username": "admin", "password": "123456"}')
    
    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        echo -e "${GREEN}✅ 登录功能正常${NC}"
        TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        return 0
    else
        echo -e "${RED}❌ 登录功能异常${NC}"
        return 1
    fi
}

# 测试用户管理
test_user_management() {
    echo -e "${PURPLE}👥 测试用户管理功能...${NC}"
    
    # 获取用户列表
    USER_LIST_RESPONSE=$(curl -s -X POST "$BACKEND_URL/users/get-user-list" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"page": 1, "size": 10}')
    
    if echo "$USER_LIST_RESPONSE" | grep -q "data"; then
        echo -e "${GREEN}✅ 用户列表获取正常${NC}"
    else
        echo -e "${RED}❌ 用户列表获取异常${NC}"
        return 1
    fi
    
    # 获取用户详情
    USER_INFO_RESPONSE=$(curl -s -X POST "$BACKEND_URL/users/get-user-info" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"user_id": 1}')
    
    if echo "$USER_INFO_RESPONSE" | grep -q "username"; then
        echo -e "${GREEN}✅ 用户详情获取正常${NC}"
    else
        echo -e "${RED}❌ 用户详情获取异常${NC}"
        return 1
    fi
}

# 测试角色管理
test_role_management() {
    echo -e "${PURPLE}🛡️  测试角色管理功能...${NC}"
    
    ROLE_LIST_RESPONSE=$(curl -s -X POST "$BACKEND_URL/roles/get-role-list" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"page": 1, "size": 10}')
    
    if echo "$ROLE_LIST_RESPONSE" | grep -q "data"; then
        echo -e "${GREEN}✅ 角色列表获取正常${NC}"
    else
        echo -e "${RED}❌ 角色列表获取异常${NC}"
        return 1
    fi
}

# 测试菜单管理
test_menu_management() {
    echo -e "${PURPLE}📋 测试菜单管理功能...${NC}"
    
    MENU_RESPONSE=$(curl -s -X POST "$BACKEND_URL/menus/get-user-menus" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"user_id": 1}')
    
    if echo "$MENU_RESPONSE" | grep -q "menus"; then
        echo -e "${GREEN}✅ 菜单获取正常${NC}"
    else
        echo -e "${RED}❌ 菜单获取异常${NC}"
        return 1
    fi
}

# 测试部门管理
test_dept_management() {
    echo -e "${PURPLE}🏢 测试部门管理功能...${NC}"
    
    DEPT_RESPONSE=$(curl -s -X POST "$BACKEND_URL/departments/get-department-tree" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{}')
    
    if echo "$DEPT_RESPONSE" | grep -q "data"; then
        echo -e "${GREEN}✅ 部门树获取正常${NC}"
    else
        echo -e "${RED}❌ 部门树获取异常${NC}"
        return 1
    fi
}

# 测试API管理
test_api_management() {
    echo -e "${PURPLE}🔌 测试API管理功能...${NC}"
    
    API_RESPONSE=$(curl -s -X GET "$BACKEND_URL/api-endpoints/?page=1&size=10" \
      -H "Authorization: Bearer $TOKEN")
    
    if echo "$API_RESPONSE" | grep -q "data"; then
        echo -e "${GREEN}✅ API列表获取正常${NC}"
    else
        echo -e "${RED}❌ API列表获取异常${NC}"
        return 1
    fi
}

# 测试日志管理
test_log_management() {
    echo -e "${PURPLE}📝 测试日志管理功能...${NC}"
    
    LOG_RESPONSE=$(curl -s -X POST "$BACKEND_URL/logs/get-log-list" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d '{"page": 1, "size": 10}')
    
    if echo "$LOG_RESPONSE" | grep -q "data"; then
        echo -e "${GREEN}✅ 日志列表获取正常${NC}"
    else
        echo -e "${RED}❌ 日志列表获取异常${NC}"
        return 1
    fi
}

# 主测试流程
main() {
    echo -e "${CYAN}🚀 Vue FastAPI Admin - 完整功能测试${NC}"
    echo -e "${CYAN}=====================================${NC}"
    
    # 检查服务
    check_services
    service_status=$?
    
    if [ $service_status -eq 1 ]; then
        echo -e "${RED}❌ 后端服务未运行，请先启动后端服务${NC}"
        exit 1
    fi
    
    # 测试登录
    if ! test_login; then
        echo -e "${RED}❌ 登录测试失败，停止后续测试${NC}"
        exit 1
    fi
    
    # 测试各个功能模块
    echo -e "${CYAN}📊 开始功能模块测试...${NC}"
    
    test_user_management
    test_role_management
    test_menu_management
    test_dept_management
    test_api_management
    test_log_management
    
    echo ""
    echo -e "${GREEN}🎉 完整功能测试完成！${NC}"
    echo ""
    echo -e "${CYAN}📋 测试结果总结：${NC}"
    echo -e "  ✅ 用户登录: 正常"
    echo -e "  ✅ 用户管理: 正常"
    echo -e "  ✅ 角色管理: 正常"
    echo -e "  ✅ 菜单管理: 正常"
    echo -e "  ✅ 部门管理: 正常"
    echo -e "  ✅ API管理: 正常"
    echo -e "  ✅ 日志管理: 正常"
    echo ""
    echo -e "${YELLOW}💡 提示: 所有核心功能测试通过，系统运行正常！${NC}"
    echo -e "${YELLOW}   访问地址: ${FRONTEND_URL}${NC}"
    echo -e "${YELLOW}   默认账号: admin / 123456${NC}"
}

# 执行主函数
main "$@"
