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
app/
├── models/{module}.py        # 数据模型
├── schemas/{module}.py       # Pydantic Schema
├── repositories/{module}.py  # 数据访问层
├── services/{module}.py      # 业务逻辑层
└── api/{module}.py           # API 路由
```

### 前端文件
```
src/
├── api/{module}.ts           # API 接口
├── types/{module}.ts         # TypeScript 类型
└── views/{module}/
    ├── index.vue             # 列表页
    └── components/
        └── FormDialog.vue    # 表单弹窗
```

### 生成的 API 接口
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/{module} | 获取列表（分页） |
| GET | /api/{module}/{id} | 获取详情 |
| POST | /api/{module} | 创建 |
| PUT | /api/{module}/{id} | 更新 |
| DELETE | /api/{module}/{id} | 删除 |
| DELETE | /api/{module}/batch | 批量删除 |

## 代码规范
- 后端遵循四层架构
- 前端使用 Vue 3 + TypeScript
- 自动添加参数校验
- 自动添加错误处理
- 自动生成类型定义

## 注意事项
- 生成前会检查是否已存在同名模块
- 会自动读取项目技术栈配置
- 生成后需要手动注册路由
