# /crud - 一键生成 CRUD 代码

## 描述
根据数据模型一键生成完整的 CRUD 代码，包括后端四层架构和前端页面。

## 使用方式
```
/crud <模块名称> [--fields <字段定义>]
```

## 参数说明
- `模块名称`: 要生成的模块名，如 `user`、`product`
- `--fields`: 可选，字段定义，格式：`字段名:类型:描述`

## 示例
```
/crud user --fields "username:string:用户名,email:string:邮箱,status:int:状态"
```

## 生成内容

### 后端文件
```
platform-fastapi-server/
├── apitest/
│   ├── model/{module}.py         # 数据模型 (SQLModel)
│   ├── schemas/{module}.py       # Pydantic Schema
│   ├── service/{module}_service.py # 业务逻辑层
│   └── api/{module}Controller.py # API 控制器
└── core/                     # 核心组件
```

### 前端文件
```
platform-vue-web/src/
├── views/{module}/
│   ├── {Module}List.vue     # 列表页
│   ├── {Module}Form.vue     # 表单弹窗
│   ├── {module}.js          # API 接口定义
│   └── components/          # 模块私有组件
└── axios.js                 # HTTP 客户端配置
```

### 生成的 API 接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /{Module}/queryByPage | 分页查询 |
| GET | /{Module}/queryById | 按ID查询 |
| POST | /{Module}/insert | 新增 |
| PUT | /{Module}/update | 更新 |
| DELETE | /{Module}/delete | 删除 |
| POST | /{Module}/batchDelete | 批量删除 |

## 代码规范
- 后端遵循四层架构（Controller → Service → Model → Schema）
- 前端使用 Vue 3 + JavaScript + Element Plus
- 自动添加参数校验
- 自动添加错误处理
- 统一响应格式

## 注意事项
- 生成前会检查是否已存在同名模块
- 会自动读取项目技术栈配置
- 生成后需要手动注册路由
