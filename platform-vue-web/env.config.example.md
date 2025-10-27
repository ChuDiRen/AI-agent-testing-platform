# 环境变量配置说明

## LangGraph 配置

在项目根目录创建 `.env` 文件，添加以下配置：

```bash
# LangGraph API 服务地址
# 本地开发环境
VITE_LANGGRAPH_API_URL=http://localhost:2024

# 生产环境示例
# VITE_LANGGRAPH_API_URL=https://your-langgraph-server.com

# LangGraph Assistant ID
# 这是您在 LangGraph 中配置的 Assistant 或 Graph ID
VITE_LANGGRAPH_ASSISTANT_ID=agent

# LangSmith API Key（可选）
# 如果您使用 LangSmith 进行追踪和调试，请填写 API Key
VITE_LANGSMITH_API_KEY=lsv2_pt_your_api_key_here
# 如果不使用，保持为空即可
# VITE_LANGSMITH_API_KEY=
```

## 配置步骤

### 1. 创建 .env 文件

```bash
cd platform-vue-web
touch .env  # Linux/Mac
# 或者在 Windows 中手动创建 .env 文件
```

### 2. 复制配置内容

将上述配置内容复制到 `.env` 文件中。

### 3. 修改配置值

根据您的实际情况修改配置值：

- `VITE_LANGGRAPH_API_URL`: LangGraph 服务器地址
- `VITE_LANGGRAPH_ASSISTANT_ID`: Assistant ID（可在 LangGraph 控制台查看）
- `VITE_LANGSMITH_API_KEY`: LangSmith API Key（可选）

### 4. 重启开发服务器

修改 `.env` 文件后，需要重启开发服务器才能生效：

```bash
# 停止当前服务器 (Ctrl+C)
# 重新启动
pnpm dev
```

## 验证配置

启动项目后，访问 **LangGraph 智能对话** 页面，点击右上角的 **设置** 按钮，查看连接状态。

- ✅ **已连接**: 配置正确
- ❌ **未连接**: 请检查配置和网络连接

## 常见问题

### Q: 如何获取 LangSmith API Key？

A: 访问 [LangSmith](https://smith.langchain.com)，注册账号后在设置中创建 API Key。

### Q: 必须配置 LangSmith API Key 吗？

A: 不是必须的。如果您只是在本地开发环境使用 LangGraph，可以不配置。生产环境建议配置以获得更好的追踪和调试支持。

### Q: 修改配置后不生效？

A: 请确保：
1. `.env` 文件位于 `platform-vue-web` 目录下
2. 配置项以 `VITE_` 开头
3. 重启了开发服务器

### Q: CORS 跨域错误怎么办？

A: 
1. 检查 LangGraph 服务器的 CORS 配置
2. 在 `vite.config.js` 中配置代理：

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/langgraph': {
        target: 'http://localhost:2024',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/langgraph/, '')
      }
    }
  }
})
```

然后修改 `.env`:
```bash
VITE_LANGGRAPH_API_URL=/langgraph
```

## 安全提示

⚠️ **重要**: 
- 不要将 `.env` 文件提交到 Git 仓库
- 不要在代码中硬编码 API Key
- 生产环境使用环境变量或密钥管理服务

