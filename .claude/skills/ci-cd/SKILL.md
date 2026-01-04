# CI/CD 流程技能

## 触发条件
- 关键词：CI/CD、持续集成、持续部署、GitHub Actions、流水线、自动化部署
- 场景：当用户需要配置或优化 CI/CD 流程时

## 核心规范

### 规范1：GitHub Actions 基础配置

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.11"
  NODE_VERSION: "18"

jobs:
  lint:
    name: Code Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Install dependencies
        run: |
          pip install ruff black isort
      
      - name: Run linters
        run: |
          ruff check .
          black --check .
          isort --check-only .

  test:
    name: Run Tests
    runs-on: ubuntu-latest
    needs: lint
    
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: test_db
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run tests
        env:
          DATABASE_URL: mysql+pymysql://root:root@localhost:3306/test_db
        run: |
          pytest tests/ -v --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### 规范2：多阶段构建流水线

```yaml
# .github/workflows/deploy.yml
name: Deploy Pipeline

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    outputs:
      image_tag: ${{ steps.meta.outputs.tags }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Docker meta
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha,prefix=
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    name: Deploy to Staging
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - name: Deploy to staging server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /app
            docker pull ${{ needs.build.outputs.image_tag }}
            docker-compose up -d

  deploy-production:
    name: Deploy to Production
    needs: [build, deploy-staging]
    runs-on: ubuntu-latest
    environment: production
    if: startsWith(github.ref, 'refs/tags/v')
    
    steps:
      - name: Deploy to production
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.SSH_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /app
            docker pull ${{ needs.build.outputs.image_tag }}
            docker-compose up -d --no-deps app
```

### 规范3：前端 CI/CD

```yaml
# .github/workflows/frontend.yml
name: Frontend CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend.yml'

defaults:
  run:
    working-directory: frontend

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        run: npm ci
      
      - name: Type check
        run: npm run type-check
      
      - name: Lint
        run: npm run lint
      
      - name: Build
        run: npm run build
        env:
          VITE_API_URL: ${{ vars.API_URL }}
      
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: frontend/dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
      - name: Download artifact
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist
      
      - name: Deploy to CDN
        run: |
          # 部署到 CDN 或静态托管服务
          echo "Deploying to CDN..."
```

### 规范4：数据库迁移

```yaml
# .github/workflows/migration.yml
name: Database Migration

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options:
          - staging
          - production
      action:
        description: 'Migration action'
        required: true
        type: choice
        options:
          - upgrade
          - downgrade

jobs:
  migrate:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install alembic sqlmodel pymysql
      
      - name: Run migration
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: |
          if [ "${{ inputs.action }}" = "upgrade" ]; then
            alembic upgrade head
          else
            alembic downgrade -1
          fi
```

### 规范5：PR 检查

```yaml
# .github/workflows/pr-check.yml
name: PR Check

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  check:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Check commit messages
        uses: wagoid/commitlint-github-action@v5
      
      - name: Check PR title
        uses: amannn/action-semantic-pull-request@v5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Check for conflicts
        run: |
          git fetch origin main
          git merge-tree $(git merge-base HEAD origin/main) HEAD origin/main
      
      - name: Comment test coverage
        uses: MishaKav/pytest-coverage-comment@main
        with:
          pytest-coverage-path: ./coverage.xml
          title: 测试覆盖率报告
```

### 规范6：环境变量管理

```yaml
# 使用 GitHub Environments
# Settings > Environments > New environment

# staging 环境变量
DATABASE_URL: mysql://user:pass@staging-db:3306/app
REDIS_URL: redis://staging-redis:6379/0
API_URL: https://api-staging.example.com

# production 环境变量
DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
REDIS_URL: ${{ secrets.PROD_REDIS_URL }}
API_URL: https://api.example.com

# 在 workflow 中使用
jobs:
  deploy:
    environment: production
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### 规范7：通知配置

```yaml
# 添加到 workflow 末尾
  notify:
    needs: [deploy-production]
    runs-on: ubuntu-latest
    if: always()
    
    steps:
      - name: Send notification
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          fields: repo,message,commit,author,action,eventName,ref,workflow
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
        if: always()
```

## 禁止事项
- ❌ 在日志中输出敏感信息
- ❌ 硬编码密钥和凭证
- ❌ 跳过测试直接部署
- ❌ 生产环境自动部署无审批
- ❌ 不做回滚准备

## 检查清单
- [ ] 是否配置了代码检查
- [ ] 是否有自动化测试
- [ ] 是否有多环境部署
- [ ] 是否有部署审批流程
- [ ] 是否有失败通知
- [ ] 是否有回滚机制
