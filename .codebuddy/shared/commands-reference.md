# 快捷命令参考

## 项目管理命令

| 命令 | 功能描述 | 调用Agent | 示例 |
|------|---------|-----------|------|
| `/start-project` | 启动新项目 | team-orchestrator | `/start-project mobile-h5 --backend=python` |
| `/analyze-requirement` | 分析需求 | product-manager | `/analyze-requirement 移动端H5商城` |
| `/design-prototype` | 设计原型 | frontend-developer | `/design-prototype 首页、商品列表` |
| `/split-tasks` | 拆分任务 | product-manager | `/split-tasks --scope=both` |

## 开发命令

| 命令 | 功能描述 | 调用Agent | 示例 |
|------|---------|-----------|------|
| `/generate-api-doc` | 生成API文档 | backend-developer | `/generate-api-doc --from-frontend` |
| `/develop-frontend` | 前端开发 | frontend-developer | `/develop-frontend TASK001` |
| `/develop-backend` | 后端开发 | backend-developer | `/develop-backend TASK006` |

## 测试命令

| 命令 | 功能描述 | 调用Agent | 示例 |
|------|---------|-----------|------|
| `/test-api` | API测试 | test-automator | `/test-api --module=user --coverage` |
| `/test-e2e` | E2E测试 | test-automator | `/test-e2e --scenario=购物车 --headed` |

## 部署命令

| 命令 | 功能描述 | 调用Agent | 示例 |
|------|---------|-----------|------|
| `/deploy` | 部署项目 | deployment-specialist | `/deploy --env=production --method=docker` |

## 调试命令

| 命令 | 功能描述 | 调用Agent | 示例 |
|------|---------|-----------|------|
| `/debug` | 调试问题 | debugger | `/debug "用户登录接口返回500错误"` |
