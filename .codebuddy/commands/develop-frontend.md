---
description: 前端开发命令
---

# 命令：develop-frontend

## 功能描述

执行前端开发任务，按照Vue3开发规范实现前端功能。

## 使用方式

```
/develop-frontend <任务编号>
```

或

```
/develop-frontend <功能描述>
```

## 参数说明

- `--task=TASK001` - 指定任务编号
- `--component=ComponentName` - 开发指定组件
- `--page=PageName` - 开发指定页面
- `--with-tests` - 同时编写测试
- `--review` - 开发完成后进行代码审查

## 执行流程

1. **任务确认**：
   - 读取任务描述
   - 确认验收标准
   - 检查依赖任务状态

2. **代码开发**：
   - 遵循Vue3开发规范
   - 使用Composition API
   - 集成UI组件库
   - 实现API调用

3. **代码质量**：
   - 添加类型注解（TypeScript）
   - 编写单元测试
   - 添加代码注释
   - 遵循代码规范

4. **自测验证**：
   - 本地运行验证
   - 检查控制台错误
   - 验证功能完整性

5. **更新状态**：
   - 更新任务状态
   - 标记验收清单

## 开发规范

### 项目结构
```
src/
├── api/           # API接口定义
├── assets/        # 静态资源
├── components/    # 公共组件
├── composables/   # 组合式函数
├── router/        # 路由配置
├── stores/        # 状态管理（Pinia）
├── styles/        # 样式文件
├── types/         # TypeScript类型定义
├── utils/         # 工具函数
└── views/         # 页面组件
```

### 代码规范

#### 组件开发
- 使用Composition API
- `<script setup>`语法
- TypeScript类型注解
- Props和Emits类型定义

#### 状态管理
- 使用Pinia进行状态管理
- 按功能模块划分Store
- 使用TypeScript定义State

#### API调用
- API接口定义在 `src/api/` 目录
- 使用Axios封装HTTP请求
- 支持Mock数据开关
- 统一错误处理

#### 样式规范
- 使用Tailwind CSS
- 组件内样式使用Scoped CSS
- 全局样式在 `styles/` 目录

## 示例

```
/develop-frontend TASK001
```

```
/develop-frontend --page=ProductList --with-tests
```

## 输出示例

```markdown
【前端开发完成】

## 开发内容
- 页面：ProductList.vue
- 组件：ProductCard.vue, FilterBar.vue
- API：product.ts
- 测试：ProductList.spec.ts

## 代码质量
- ✅ TypeScript类型完整
- ✅ 单元测试覆盖率达到80%
- ✅ 代码审查通过
- ✅ 本地运行测试通过

## 验收标准
- [x] 功能正常工作
- [x] 代码符合规范
- [x] 通过代码审查
- [x] 通过单元测试

## 下一步
1. 启动本地开发服务器：`pnpm dev`
2. 访问 http://localhost:5173 查看效果
3. 手动测试所有功能点
```

## 相关命令

- `/split-tasks` - 查看任务列表
- `/develop-backend` - 后端开发
- `/test-e2e` - E2E测试
