# AI Agent Testing Platform - FastAPI Backend

基于 FastAPI + SQLModel 的 AI 智能体测试平台后端服务

## 技术栈

- **Web框架**: FastAPI 0.104.1
- **ORM**: SQLModel 0.0.14
- **数据库**: MySQL / SQLite (可配置切换)
- **认证**: python-jose (JWT)
- **对象存储**: MinIO
- **配置管理**: Pydantic Settings

## 项目结构

```
platform-flask-server/
├── app.py                 # FastAPI应用入口
├── run.py                 # 启动脚本
├── requirements.txt       # 项目依赖
├── config/               # 配置文件
│   ├── dev_settings.py   # 开发环境配置
│   ├── test_settings.py  # 测试环境配置
│   └── prod_settings.py  # 生产环境配置
├── core/                 # 核心模块
│   ├── database.py       # 数据库连接和会话管理
│   ├── dependencies.py   # 依赖注入函数
│   ├── JwtUtil.py        # JWT工具类
│   ├── MinioUtils.py     # MinIO对象存储工具
│   └── resp_model.py     # 统一响应模型
├── schemas/              # Pydantic数据模型
│   ├── user_schema.py
│   ├── api_project_schema.py
│   ├── api_database_schema.py
│   ├── api_keyword_schema.py
│   ├── api_meta_schema.py
│   └── operation_type_schema.py
├── login/                # 登录模块
│   └── api/
│       └── LoginController.py
├── sysmanage/            # 系统管理模块
│   ├── model/
│   │   └── user.py       # 用户模型
│   └── api/
│       └── UserController.py
└── apitest/              # API测试模块
    ├── model/            # 数据模型
    │   ├── ApiProjectModel.py
    │   ├── ApiDbBaseModel.py
    │   ├── ApiKeyWordModel.py
    │   ├── ApiMetaModel.py
    │   └── ApiOperationTypeModel.py
    └── api/              # 接口控制器
        ├── ApiProjectContoller.py
        ├── ApiDbBaseController.py
        ├── ApiKeyWordController.py
        ├── ApiMetaController.py
        └── ApiOperationTypeController.py
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### 数据库配置（支持MySQL和SQLite切换）

编辑 `config/dev_settings.py` 配置文件：

**使用SQLite（默认，开箱即用）**：
```python
DB_TYPE = "sqlite"  # 使用SQLite
SQLITE_DATABASE = "./data/ai_agent.db"  # SQLite数据库文件路径
```

**使用MySQL**：
```python
DB_TYPE = "mysql"  # 使用MySQL
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "platfrom_back"
```

### 其他配置

```python
# JWT密钥配置
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# MinIO配置
MINIO_CLIENT_URL = "http://localhost:9000"
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_SECURE = False

# 关键字文件目录
KEY_WORDS_DIR = "./keywords"
```

### 环境切换

- **开发环境**: 使用 `config/dev_settings.py` (默认SQLite)
- **测试环境**: 使用 `config/test_settings.py` (默认SQLite)
- **生产环境**: 使用 `config/prod_settings.py` (默认MySQL)

## 启动应用

### 开发模式（热重载）

```bash
python run.py
```

或

```bash
python app.py
```

### 生产模式

```bash
uvicorn app:application --host 0.0.0.0 --port 8000 --workers 4
```

## API文档

启动应用后访问：

- **交互式文档 (Swagger UI)**: http://localhost:8000/docs
- **备选文档 (ReDoc)**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 主要功能模块

### 1. 用户认证

- `POST /login` - 用户登录

### 2. 用户管理

- `POST /user/queryByPage` - 分页查询用户
- `GET /user/queryById` - 根据ID查询用户
- `POST /user/insert` - 新增用户
- `PUT /user/update` - 更新用户
- `DELETE /user/delete` - 删除用户

### 3. API项目管理

- `POST /ApiProject/queryByPage` - 分页查询项目
- `GET /ApiProject/queryById` - 根据ID查询项目
- `GET /ApiProject/queryAll` - 查询所有项目
- `POST /ApiProject/insert` - 新增项目
- `PUT /ApiProject/update` - 更新项目
- `DELETE /ApiProject/delete` - 删除项目

### 4. API数据库配置管理

- `POST /ApiDbBase/queryByPage` - 分页查询数据库配置
- `GET /ApiDbBase/queryById` - 根据ID查询配置
- `POST /ApiDbBase/insert` - 新增配置（带唯一性校验）
- `PUT /ApiDbBase/update` - 更新配置
- `DELETE /ApiDbBase/delete` - 删除配置

### 5. API关键字管理

- `GET /ApiKeyWord/queryAll` - 查询所有关键字
- `POST /ApiKeyWord/queryByPage` - 分页查询关键字
- `GET /ApiKeyWord/queryById` - 根据ID查询关键字
- `POST /ApiKeyWord/insert` - 新增关键字（带唯一性校验）
- `PUT /ApiKeyWord/update` - 更新关键字（带唯一性校验）
- `DELETE /ApiKeyWord/delete` - 删除关键字
- `POST /ApiKeyWord/keywordFile` - 生成关键字文件

### 6. API元数据管理（文件管理）

- `GET /ApiMeta/queryAll` - 查询所有元数据
- `POST /ApiMeta/queryByPage` - 分页查询元数据
- `GET /ApiMeta/queryById` - 根据ID查询元数据
- `POST /ApiMeta/insert` - 上传文件并新增元数据
- `PUT /ApiMeta/update` - 更新元数据
- `DELETE /ApiMeta/delete` - 删除元数据
- `GET /ApiMeta/downloadFile` - 获取文件下载地址

### 7. 操作类型管理

- `GET /OperationType/queryAll` - 查询所有操作类型
- `POST /OperationType/queryByPage` - 分页查询操作类型
- `GET /OperationType/queryById` - 根据ID查询操作类型
- `POST /OperationType/insert` - 新增操作类型
- `PUT /OperationType/update` - 更新操作类型
- `DELETE /OperationType/delete` - 删除操作类型

## 数据库迁移

首次启动时，应用会自动创建所有数据表。

## 环境变量

支持通过 `.env` 文件配置环境变量：

```env
# 数据库类型选择
DB_TYPE=sqlite

# SQLite配置（DB_TYPE=sqlite时使用）
SQLITE_DATABASE=./data/ai_agent.db

# MySQL配置（DB_TYPE=mysql时使用）
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=platfrom_back

# JWT配置
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# MinIO配置
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=False
```

## 技术特性

- ✅ 同步SQLModel，保持与原Flask代码接近
- ✅ 支持MySQL和SQLite数据库切换
- ✅ 依赖注入（数据库会话、JWT认证、MinIO客户端）
- ✅ 统一响应格式
- ✅ 自动API文档生成
- ✅ 数据验证（Pydantic）
- ✅ 类型提示
- ✅ 文件上传下载
- ✅ JWT认证
- ✅ CORS支持
- ✅ 唯一性校验

## 开发规范

- 所有注释位于代码右侧，格式为 `# 注释`
- 使用类型注解
- 遵循PEP 8规范
- 保持代码简洁高效

## 版本信息

- **版本**: 2.0.0
- **框架**: FastAPI
- **ORM**: SQLModel
- **Python**: 3.8+

## 注意事项

1. **数据库选择**：
   - 开发/测试环境推荐使用SQLite（开箱即用，无需安装）
   - 生产环境推荐使用MySQL（性能更好，支持并发）
2. 使用MySQL时，确保MySQL数据库已启动并可访问
3. 确保MinIO服务已启动（如使用文件上传功能）
4. 生产环境请修改CORS配置，指定具体允许的域名
5. 生产环境请使用强密码和安全的SECRET_KEY
6. 建议使用虚拟环境进行开发

## 迁移说明

本项目已从 Flask + Flask-SQLAlchemy 迁移至 FastAPI + SQLModel：

- ✅ 保持原有功能不变
- ✅ 保持原有目录结构
- ✅ 保持原有API路径
- ✅ 保持原有响应格式
- ✅ 使用同步方式，降低迁移成本
- ✅ 所有业务逻辑保持一致

