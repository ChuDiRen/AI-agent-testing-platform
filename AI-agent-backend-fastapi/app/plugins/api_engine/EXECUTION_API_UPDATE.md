# API引擎执行历史功能完善

## 问题描述
前端执行历史页面显示"No Data"，控制台报404错误。原因是后端缺少执行历史列表查询接口。

## 解决方案
添加完整的执行记录CRUD接口，包括：
- 列表查询（支持分页、筛选）
- 详情查询
- 删除记录

## 修改内容

### 1. 后端修改

#### 新增文件
- `app/plugins/api_engine/services/execution_service.py` - 执行记录服务层

#### 修改文件

**app/plugins/api_engine/api/execution.py**
- 新增 `GET /executions` - 获取执行历史列表
- 新增 `GET /executions/{execution_id}` - 获取执行详情
- 新增 `DELETE /executions/{execution_id}` - 删除执行记录
- 修改 `GET /{task_id}/status` → `GET /task/{task_id}/status` - 查询任务状态

**app/plugins/api_engine/services/__init__.py**
- 导出 `ExecutionService`

**app/plugins/api_engine/init_db.py**
- 添加示例执行记录初始化（成功、失败、运行中各1条）

### 2. 前端修改

**src/plugins/api-engine/api/execution.ts**
- 更新 `Execution` 接口定义，与后端数据结构匹配
- 修改 `getExecutionStatus` 路由：`/executions/${taskId}/status` → `/executions/task/${taskId}/status`
- 新增 `deleteExecution` 方法

**src/plugins/api-engine/views/ExecutionHistory.vue**
- 移除套件筛选（执行记录不直接关联套件）
- 更新状态选项：`passed` → `success`
- 新增步骤统计列显示
- 更新时间字段：`start_time/end_time` → `executed_at/finished_at`
- 新增删除按钮和删除功能
- 更新详情对话框字段映射

**src/plugins/api-engine/store/index.ts**
- 新增 `deleteExecution` action

**src/main.ts**
- 修改插件路由注册：`router.addRoute(route)` → `router.addRoute('MainLayout', route)`
- 使插件页面显示在主布局中（包含侧边栏和顶部导航）

**src/router/index.ts**
- 给MainLayout路由添加 `name: 'MainLayout'`

## API接口说明

### 获取执行历史列表
```
GET /api/v1/plugin/api-engine/executions
Query参数:
  - page: 页码（默认1）
  - page_size: 每页数量（默认20）
  - case_id: 用例ID（可选）
  - status: 执行状态（可选）pending/running/success/failed/error

响应:
{
  "success": true,
  "data": {
    "total": 10,
    "items": [...]
  }
}
```

### 获取执行详情
```
GET /api/v1/plugin/api-engine/executions/{execution_id}

响应:
{
  "success": true,
  "data": {
    "execution_id": 1,
    "case_id": 1,
    "task_id": "uuid",
    "status": "success",
    "result": {...},
    "logs": "...",
    "error_message": null,
    "duration": 2.35,
    "steps_total": 3,
    "steps_passed": 3,
    "steps_failed": 0,
    "executed_by": 1,
    "executed_at": "2025-01-15T10:00:00",
    "finished_at": "2025-01-15T10:00:02"
  }
}
```

### 删除执行记录
```
DELETE /api/v1/plugin/api-engine/executions/{execution_id}

响应:
{
  "success": true,
  "message": "删除成功"
}
```

### 查询任务状态
```
GET /api/v1/plugin/api-engine/executions/task/{task_id}/status

响应:
{
  "success": true,
  "data": {
    "task_id": "uuid",
    "status": "SUCCESS",
    "progress": 100,
    "message": "执行成功",
    "result": {...}
  }
}
```

## 数据库初始化

重新初始化数据库后，会自动创建：
- 1个示例测试套件
- 2个示例测试用例
- 3条示例执行记录（成功、失败、运行中）

## 测试步骤

1. 重启后端服务
2. 访问前端执行历史页面：`http://localhost:5173/plugin/api-engine/executions`
3. 应该能看到3条示例执行记录
4. 测试筛选、查看详情、删除功能

## 注意事项

1. 执行记录的 `task_id` 必须唯一
2. 删除执行记录不会删除关联的用例
3. 执行状态包括：pending、running、success、failed、error
4. 前端页面现在会显示在主布局中，包含侧边栏和顶部导航

