---
description: 后端开发命令
---

# 命令：develop-backend

## 功能描述

执行后端开发任务，按照选定技术栈（Java/Python）的开发规范实现后端功能。

## 使用方式

```
/develop-backend <任务编号>
```

或

```
/develop-backend <功能描述>
```

## 参数说明

- `--task=TASK001` - 指定任务编号
- `--module=ModuleName` - 开发指定模块
- `--with-tests` - 同时编写测试
- `--with-doc` - 生成API文档
- `--review` - 开发完成后进行代码审查

## 执行流程

1. **任务确认**：
   - 读取任务描述
   - 确认技术栈
   - 检查依赖任务状态

2. **代码开发**：
   - 遵循对应技术栈开发规范
   - 实现业务逻辑
   - 数据库操作
   - API接口开发

3. **代码质量**：
   - 添加类型注解
   - 编写单元测试
   - 添加代码注释
   - 遵循分层架构

4. **自测验证**：
   - 本地运行验证
   - API接口测试
   - 检查日志输出

5. **更新状态**：
   - 更新任务状态
   - 标记验收清单

## Java Spring Boot 开发规范

### 项目结构
```
src/main/java/com/company/project/
├── controller/     # 控制器层（Gateway）
├── service/        # 业务逻辑层
├── manager/        # 数据管理层
├── mapper/         # 数据访问层
├── entity/         # 实体类
├── dto/            # 数据传输对象
├── enums/          # 枚举类
├── config/         # 配置类
└── util/           # 工具类

src/main/resources/
├── mapper/         # MyBatis XML文件
└── application.yaml
```

### 分层架构

#### Controller层
- 职责：参数校验、请求路由
- 禁止编写业务逻辑
- 只能调用Service层

#### Service层
- 职责：业务逻辑实现
- 通过Manager访问数据库
- 入参返参使用DTO

#### Manager层
- 职责：数据访问和缓存封装
- 只能被Service层调用
- 调用Mapper和Redis

#### Mapper层
- 职责：数据库访问
- 继承BaseMapper
- XML文件存放SQL

### 开发原则
- 严禁使用BeanUtil.copyProperties()
- 严禁在循环中查询数据库
- Entity创建必须显式赋值所有字段
- 跨表写操作使用@Transactional

## Python FastAPI 开发规范

### 项目结构
```
app/
├── api/            # API路由层
├── services/       # 业务逻辑层
├── repositories/   # 数据访问层
├── models/         # 数据模型
│   ├── sqlalchemy/  # SQLAlchemy模型
│   └── pydantic/   # Pydantic模型
├── core/           # 核心配置
├── utils/          # 工具函数
└── main.py         # 应用入口
```

### 分层架构

#### API层
- 职责：请求处理、响应
- 禁止编写业务逻辑
- 只能调用Service层

#### Service层
- 职责：业务逻辑实现
- 通过Repository访问数据
- 支持异步操作

#### Repository层
- 职责：数据持久化
- 使用SQLAlchemy ORM
- 支持异步操作

### 开发原则
- 强制使用类型注解
- 所有I/O操作使用异步
- 使用Pydantic进行数据验证
- 遵循PEP 8编码规范

## 示例

```
/develop-backend TASK006
```

```
/develop-backend --module=User --with-tests --with-doc
```

## 输出示例

```markdown
【后端开发完成】

## 开发内容（Java Spring Boot）
- Controller: UserController.java
- Service: UserService.java
- Manager: UserManager.java
- Mapper: UserMapper.java
- Entity: User.java
- DTO: UserCreateDTO, UserResponseDTO

## 代码质量
- ✅ 遵循分层架构
- ✅ 单元测试覆盖率≥80%
- ✅ 代码审查通过
- ✅ 接口测试通过

## 验收标准
- [x] 功能正常工作
- [x] 代码符合规范
- [x] 通过代码审查
- [x] 通过单元测试

## API文档
已生成API文档到 doc/api.md

## 下一步
1. 启动应用：`mvn spring-boot:run`
2. 访问 http://localhost:8080/api-docs 查看API文档
3. 使用Postman测试接口
```

## 相关命令

- `/split-tasks` - 查看任务列表
- `/develop-frontend` - 前端开发
- `/test-api` - API测试
- `/generate-api-doc` - 生成API文档
