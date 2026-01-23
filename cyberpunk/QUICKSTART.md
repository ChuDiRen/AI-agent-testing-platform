# Cyberpunk 快速启动指南

## 前置要求

- Python 3.11+
- Node.js 18+
- pnpm（推荐）或 npm

## 快速开始

### 方法一：使用启动脚本（Windows）

双击运行 `start.bat`，按照菜单提示操作：

1. 选择 `1` - 安装后端依赖
2. 选择 `2` - 安装前端依赖
3. 配置环境变量（见下方说明）
4. 选择 `5` - 同时启动前后端

### 方法二：手动启动

#### 1. 安装后端依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境（Windows）
.\.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 配置环境变量

复制环境变量模板：

```bash
copy app\.env.example app\.env
```

编辑 `app\.env` 文件，填入你的配置：

```env
# 必填项
OPENAI_API_KEY=your_openai_api_key_here

# 可选项（使用默认值即可）
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
```

#### 3. 启动后端

```bash
# 确保虚拟环境已激活
python run.py
```

后端服务将运行在：
- API 服务：http://localhost:8000
- API 文档：http://localhost:8000/docs

#### 4. 安装前端依赖

打开新的终端窗口：

```bash
cd web

# 安装 pnpm（如果未安装）
npm install -g pnpm

# 安装依赖
pnpm install
```

#### 5. 启动前端

```bash
# 在 web 目录下
pnpm dev
```

前端应用将运行在：http://localhost:5173

## 访问应用

1. 打开浏览器访问：http://localhost:5173
2. 开始使用 Cyberpunk 平台！

## 常见问题

### Q: 后端启动失败，提示找不到模块？

A: 确保已激活虚拟环境并安装了所有依赖：

```bash
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Q: 前端启动失败？

A: 尝试删除 `node_modules` 并重新安装：

```bash
cd web
rm -rf node_modules
pnpm install
```

### Q: API 调用失败？

A: 检查以下几点：
1. `app\.env` 文件中的 `OPENAI_API_KEY` 是否正确
2. 网络连接是否正常
3. OpenAI API 配额是否充足

### Q: 端口被占用？

A: 修改端口配置：
- 后端：编辑 `run.py` 中的 `port` 参数
- 前端：编辑 `web/vite.config.ts` 中的 `server.port`

## 开发模式

### 后端热重载

后端使用 `uvicorn` 的 `reload=True` 选项，修改代码后会自动重启。

### 前端热重载

前端使用 Vite，修改代码后会自动刷新浏览器。

## 下一步

- 查看 [README.md](README.md) 了解详细功能
- 访问 http://localhost:8000/docs 查看 API 文档
- 探索前端各个功能模块

## 技术支持

如有问题，请查看：
- 项目 README.md
- API 文档：http://localhost:8000/docs
- 后端日志：`app/log/` 目录
