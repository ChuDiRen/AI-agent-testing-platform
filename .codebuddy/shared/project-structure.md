# 标准项目结构

## 前后端分离项目

```
project-name/
├── frontend/          # 前端项目
│   ├── src/
│   │   ├── api/            # API接口定义
│   │   ├── assets/         # 静态资源
│   │   ├── components/     # 公共组件
│   │   ├── composables/    # 组合式函数
│   │   ├── router/         # 路由配置
│   │   ├── stores/         # 状态管理
│   │   ├── types/          # TypeScript类型
│   │   ├── utils/          # 工具函数
│   │   └── views/          # 页面组件
│   ├── package.json
│   └── vite.config.ts
└── backend/           # 后端项目
    ├── app/                # Python FastAPI
    │   ├── api/            # API路由
    │   ├── services/       # 业务逻辑
    │   ├── repositories/   # 数据访问
    │   ├── models/         # 数据模型
    │   ├── core/           # 核心配置
    │   └── utils/          # 工具函数
    ├── tests/              # 测试文件
    ├── alembic/            # 数据库迁移
    ├── pyproject.toml
    └── main.py
```

## Java Spring Boot 后端结构

```
backend/
├── src/main/java/com/example/
│   ├── controller/         # API控制器
│   ├── service/            # 业务逻辑
│   │   └── impl/
│   ├── mapper/             # MyBatis Mapper
│   ├── entity/             # 数据实体
│   ├── dto/                # 数据传输对象
│   ├── vo/                 # 视图对象
│   ├── config/             # 配置类
│   ├── exception/          # 异常处理
│   └── utils/              # 工具类
├── src/main/resources/
│   ├── mapper/             # MyBatis XML
│   └── application.yml
├── src/test/               # 测试代码
└── pom.xml
```

## 测试目录结构

```
tests/
├── api/                    # API测试
│   ├── conftest.py
│   ├── test_user.py
│   └── test_product.py
├── e2e/                    # E2E测试
│   ├── tests/
│   │   ├── login.spec.ts
│   │   └── cart.spec.ts
│   └── playwright.config.ts
└── reports/                # 测试报告
    ├── api-test-report.html
    └── e2e-test-report.html
```
