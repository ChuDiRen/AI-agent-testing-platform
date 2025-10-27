# LangGraph 集成文档

## 简介

本项目已成功集成 LangGraph SDK，提供高级 AI 对话功能。使用 Element-Plus-X 组件库构建了专业的聊天界面。

## 功能特性

### ✨ 核心功能

- **流式对话** - 实时打字机效果，体验流畅
- **对话历史** - 支持创建、切换、删除多个对话线程
- **工具调用展示** - 可视化 AI 工具调用过程
- **中断处理** - 支持人机交互确认流程
- **Artifact 展示** - 侧边栏展示生成的文档、代码等
- **响应式设计** - PC 和移动端自适应

### 🎨 UI 组件

使用 [Element-Plus-X](https://element-plus-x.com) 组件库：

- `EditorSender` - 多模态编辑输入框
- `Bubble` / `BubbleList` - 对话气泡和列表
- `Typewriter` - 打字机效果
- `Thinking` - 思考中动画
- `Conversations` - 会话管理

## 快速开始

### 1. 环境配置

创建 `.env` 文件（或复制 `.env.example`）：

```bash
# LangGraph 配置
VITE_LANGGRAPH_API_URL=http://localhost:2024
VITE_LANGGRAPH_ASSISTANT_ID=agent
VITE_LANGSMITH_API_KEY=your_api_key_here
```

### 2. 安装依赖

依赖已经安装，包括：

- `vue-element-plus-x` - Element Plus 扩展组件库
- `@langchain/langgraph-sdk` - LangGraph SDK
- `@langchain/core` - LangChain 核心
- `uuid` - UUID 生成

### 3. 启动项目

```bash
cd platform-vue-web
pnpm dev
```

访问 `http://localhost:5173`，点击左侧菜单 **AI 助手 > LangGraph 智能对话**。

## 使用指南

### 创建新对话

1. 点击左侧边栏的 **新对话** 按钮
2. 系统会自动创建一个新的对话线程
3. 在输入框中输入问题并发送

### 切换对话

点击左侧边栏中的对话项即可切换到该对话。

### 删除对话

将鼠标悬停在对话项上，点击右侧的删除图标。

### 发送消息

- **Enter** 键：发送消息
- **Shift + Enter**：换行

### 停止生成

如果 AI 正在生成回复，点击输入框右侧的停止按钮可以中断生成。

## 项目结构

```
platform-vue-web/src/
├── api/
│   └── langgraph.js                 # LangGraph API 集成层
├── composables/
│   ├── useLangGraphStream.js        # 流式通信 Composable
│   └── useLangGraphThread.js        # 线程管理 Composable
└── views/aiassistant/langgraph/
    ├── LangGraphChat.vue            # 主聊天界面
    └── components/
        ├── ToolCallDisplay.vue      # 工具调用展示
        ├── InterruptHandler.vue     # 中断处理
        └── ArtifactPanel.vue        # Artifact 侧边栏
```

## API 说明

### LangGraph API 层 (`api/langgraph.js`)

```javascript
import { 
  createLangGraphClient,  // 创建客户端
  streamMessages,         // 流式消息
  getThreads,            // 获取线程列表
  createThread,          // 创建新线程
  deleteThread,          // 删除线程
  getThreadState         // 获取线程状态
} from '@/api/langgraph'
```

### Composables

#### `useLangGraphStream`

管理流式消息通信：

```javascript
const {
  messages,              // 消息列表
  isSending,            // 是否正在发送
  isThinking,           // 是否正在思考
  sendMessage,          // 发送消息
  stopGeneration,       // 停止生成
  clearMessages,        // 清空消息
  loadThreadHistory     // 加载历史
} = useLangGraphStream()
```

#### `useLangGraphThread`

管理对话线程：

```javascript
const {
  threads,              // 线程列表
  currentThreadId,      // 当前线程 ID
  currentThread,        // 当前线程对象
  fetchThreads,         // 获取线程列表
  createNewThread,      // 创建新线程
  switchThread,         // 切换线程
  removeThread          // 删除线程
} = useLangGraphThread()
```

## 组件说明

### LangGraphChat.vue

主聊天界面，整合了所有功能模块。

**Props**: 无

**主要功能**:
- 侧边栏对话列表
- 消息展示区域
- 输入框和工具栏
- 设置面板

### ToolCallDisplay.vue

展示 AI 工具调用的详细信息。

**Props**:
- `calls` (Array): 工具调用列表

**展示内容**:
- 工具名称和状态
- 调用参数
- 执行结果
- 错误信息

### InterruptHandler.vue

处理 AI 中断，需要用户确认的场景。

**Props**:
- `interrupt` (Object): 中断信息对象

**Events**:
- `confirm`: 用户确认
- `cancel`: 用户取消

### ArtifactPanel.vue

侧边栏展示生成的内容（文档、代码等）。

**Props**:
- `modelValue` (Boolean): 显示/隐藏
- `title` (String): 标题
- `content` (String): 内容
- `contentType` (String): 内容类型 (text/markdown/code)
- `language` (String): 代码语言

**功能**:
- 复制内容
- 下载文件
- Markdown 渲染

## 自定义配置

### 修改打字机速度

在 `LangGraphChat.vue` 中：

```vue
<Typewriter 
  v-if="message.streaming"
  :text="message.content"
  :speed="30"  <!-- 修改这里，单位：毫秒/字符 -->
/>
```

### 修改主题颜色

在 `platform-vue-web/src/styles/theme.css` 中修改 CSS 变量。

### 添加自定义工具

在 `ToolCallDisplay.vue` 中扩展工具类型和展示逻辑。

## 常见问题

### 1. 无法连接到 LangGraph 服务器

**解决方案**:
- 检查 `.env` 文件中的 `VITE_LANGGRAPH_API_URL` 是否正确
- 确保 LangGraph 服务器已启动
- 检查网络连接和防火墙设置

### 2. 消息发送后没有响应

**解决方案**:
- 检查浏览器控制台是否有错误
- 确认 `VITE_LANGGRAPH_ASSISTANT_ID` 配置正确
- 检查 LangGraph 服务器日志

### 3. 样式显示异常

**解决方案**:
- 确认 Element-Plus-X 样式已正确导入
- 清除浏览器缓存
- 检查 CSS 优先级冲突

### 4. 中文输入法问题

Element-Plus-X 的 `EditorSender` 已经处理了中文输入法兼容性。

## 技术栈

- **Vue 3.2.47** - 渐进式 JavaScript 框架
- **Element Plus 2.6.3** - UI 组件库
- **Element-Plus-X** - AI 聊天组件扩展
- **LangGraph SDK** - AI 对话 SDK
- **Vite 4.3.9** - 构建工具

## 参考资源

- [Element-Plus-X 官方文档](https://element-plus-x.com)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [Element Plus 文档](https://element-plus.org)

## 未来计划

- [ ] 支持文件上传（多模态输入）
- [ ] 支持语音输入/输出
- [ ] 添加对话导出功能
- [ ] 支持对话分享
- [ ] 集成更多 AI 模型
- [ ] 添加对话搜索功能
- [ ] 支持代码高亮（集成 Prism.js）

## 贡献

如有问题或建议，欢迎提交 Issue 或 Pull Request。

## 许可证

MIT License

