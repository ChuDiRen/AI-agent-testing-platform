# LangGraph 智能对话 - 快速启动指南

## 🚀 5分钟快速上手

### 步骤 1: 配置环境变量

在 `platform-vue-web` 目录下创建 `.env` 文件：

```bash
# 复制以下内容到 .env 文件
VITE_LANGGRAPH_API_URL=http://localhost:2024
VITE_LANGGRAPH_ASSISTANT_ID=agent
VITE_LANGSMITH_API_KEY=
```

### 步骤 2: 启动项目

```bash
cd platform-vue-web
pnpm dev
```

### 步骤 3: 访问功能

1. 打开浏览器访问 `http://localhost:5173`
2. 使用账号密码登录（如果已登录可跳过）
3. 点击左侧菜单 **AI 助手 > LangGraph 智能对话**
4. 点击 **新对话** 按钮创建对话
5. 在输入框中输入问题并发送

## ✅ 功能验证

### 测试流式对话

1. 创建新对话
2. 输入: "你好，请介绍一下自己"
3. 观察 AI 回复是否有打字机效果

### 测试对话历史

1. 创建多个对话
2. 在不同对话间切换
3. 验证消息是否正确保存

### 测试工具调用（如果您的 Agent 支持）

1. 输入需要调用工具的问题
2. 观察工具调用过程的展示
3. 查看工具执行结果

## 🎯 使用技巧

### 快捷键

- `Enter`: 发送消息
- `Shift + Enter`: 换行
- `Ctrl + C`: 停止生成（开发中）

### 菜单功能

- **新对话**: 创建新的对话线程
- **切换对话**: 点击左侧对话项切换
- **删除对话**: 悬停在对话项上，点击删除图标
- **设置**: 查看连接状态和配置信息

### 消息操作

- **查看工具调用**: 点击工具调用卡片展开详情
- **复制内容**: 在 Artifact 侧边栏点击复制按钮
- **下载内容**: 在 Artifact 侧边栏点击下载按钮

## 🔧 故障排查

### 问题 1: 连接失败

**现象**: 设置页面显示"未连接"

**解决方案**:
1. 检查 `.env` 文件是否正确配置
2. 确认 LangGraph 服务器是否启动
3. 检查网络连接
4. 查看浏览器控制台错误信息

```bash
# 检查 LangGraph 服务器状态
curl http://localhost:2024/info
```

### 问题 2: 发送消息无响应

**现象**: 点击发送后没有任何反应

**解决方案**:
1. 打开浏览器开发者工具（F12）
2. 查看 Console 标签页的错误信息
3. 查看 Network 标签页的网络请求
4. 确认 Assistant ID 是否正确

### 问题 3: 打字机效果不流畅

**现象**: 消息一次性全部显示，没有逐字显示

**解决方案**:
1. 检查 LangGraph 服务器是否支持流式输出
2. 查看 `streamMode` 配置是否正确
3. 检查网络连接稳定性

### 问题 4: 样式显示异常

**现象**: 界面布局错乱或样式丢失

**解决方案**:
1. 清除浏览器缓存
2. 确认 Element-Plus-X 样式是否正确加载
3. 检查是否有 CSS 冲突

```bash
# 重新安装依赖
cd platform-vue-web
rm -rf node_modules
pnpm install
```

## 📚 进阶使用

### 自定义配置

#### 修改打字机速度

编辑 `src/views/aiassistant/langgraph/LangGraphChat.vue`:

```vue
<Typewriter 
  :text="message.content"
  :speed="50"  <!-- 修改这个值，单位：毫秒/字符 -->
/>
```

#### 修改侧边栏宽度

编辑 `src/views/aiassistant/langgraph/LangGraphChat.vue`:

```css
.sidebar {
  width: 320px;  /* 默认 280px */
}
```

#### 添加自定义工具展示

编辑 `src/views/aiassistant/langgraph/components/ToolCallDisplay.vue`，根据您的工具类型自定义展示逻辑。

### 集成到现有系统

如果您想在其他页面中使用 LangGraph 功能：

1. **导入 Composables**:

```javascript
import { useLangGraphStream } from '@/composables/useLangGraphStream'
import { useLangGraphThread } from '@/composables/useLangGraphThread'
```

2. **使用组件**:

```vue
<script setup>
import { EditorSender, Bubble } from 'vue-element-plus-x'
const { sendMessage, messages } = useLangGraphStream()
</script>

<template>
  <Bubble 
    v-for="msg in messages" 
    :key="msg.id"
    :type="msg.role"
  >
    {{ msg.content }}
  </Bubble>
  
  <EditorSender @submit="handleSend" />
</template>
```

### 部署到生产环境

1. **配置生产环境变量**:

创建 `.env.production`:

```bash
VITE_LANGGRAPH_API_URL=https://your-production-server.com
VITE_LANGGRAPH_ASSISTANT_ID=your_production_agent
VITE_LANGSMITH_API_KEY=your_production_key
```

2. **构建生产版本**:

```bash
pnpm build
```

3. **部署 dist 目录**到您的服务器（Nginx、Apache 等）

## 🎓 学习资源

- [Element-Plus-X 官方文档](https://element-plus-x.com)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [Vue 3 文档](https://cn.vuejs.org/)
- [Element Plus 文档](https://element-plus.org)

## 💬 获取帮助

如遇到问题：

1. 查看 [LANGGRAPH_INTEGRATION.md](./LANGGRAPH_INTEGRATION.md) 完整文档
2. 查看 [env.config.example.md](./env.config.example.md) 配置说明
3. 检查浏览器控制台错误信息
4. 提交 Issue 到项目仓库

## ⭐ 下一步

- 尝试不同的提示词
- 探索工具调用功能
- 自定义样式和主题
- 集成更多 AI 模型
- 添加语音输入/输出

祝您使用愉快！🎉

