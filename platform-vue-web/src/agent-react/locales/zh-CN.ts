// 中文语言包
export const zhCN = {
  // 应用元信息
  app: {
    title: "AI 智能体聊天",
    description: "基于 LangChain 的 AI 智能体聊天界面",
  },

  // 通用文本
  common: {
    loading: "加载中...",
    cancel: "取消",
    confirm: "确认",
    delete: "删除",
    edit: "编辑",
    save: "保存",
    send: "发送",
    copy: "复制",
    copied: "已复制",
    refresh: "刷新",
    submit: "提交",
    close: "关闭",
    search: "搜索",
    select: "选择",
    continue: "继续",
  },

  // 线程/会话相关
  thread: {
    history: "聊天历史",
    newThread: "新建对话",
    delete: "删除",
    deleteConfirm: "确定要删除这条聊天记录吗？",
    deleteMultipleConfirm: "确定要删除这 {count} 条聊天记录吗？",
    deleteSuccess: "删除成功",
    deleteFailed: "删除失败",
    batchDelete: "批量删除",
    batchMode: "批量模式",
    cancelBatch: "取消批量",
    deleteSelected: "删除选中项",
    selectAll: "全选",
    unselectAll: "取消全选",
    noThreads: "暂无聊天记录",
    threadId: "会话 ID",
    copyThreadId: "复制会话 ID",
  },

  // 消息相关
  message: {
    typeMessage: "输入您的消息...",
    scrollToBottom: "滚动到底部",
    copyContent: "复制内容",
    cancelEdit: "取消编辑",
    regenerate: "重新生成",
  },

  // 工具调用
  toolCall: {
    hide: "隐藏工具调用",
    show: "显示工具调用",
  },

  // 文件上传
  upload: {
    title: "上传 PDF 或图片",
    dragDrop: "拖放文件到此处",
    or: "或",
    browse: "浏览文件",
    uploading: "上传中...",
    uploadSuccess: "上传成功",
    uploadFailed: "上传失败",
  },

  // 配置表单
  config: {
    welcome: "欢迎使用 AI 智能体聊天！在开始之前，您需要输入部署 URL 和智能体/图谱 ID。",
    deploymentUrl: "部署 URL",
    deploymentUrlDesc: "这是您的 LangGraph 部署 URL。可以是本地或生产环境部署。",
    assistantId: "智能体/图谱 ID",
    assistantIdDesc: "这是要获取线程并在执行操作时调用的图谱 ID（可以是图谱名称）或智能体 ID。",
    apiKey: "LangSmith API 密钥",
    apiKeyDesc: "如果使用本地 LangGraph 服务器，则不需要此项。此值存储在浏览器的本地存储中，仅用于验证发送到 LangGraph 服务器的请求。",
    apiKeyPlaceholder: "lsv2_pt_...",
    required: "必填",
  },

  // 错误信息
  error: {
    general: "发生错误，请重试。",
    connectionFailed: "无法连接到 LangGraph 服务器",
    connectionFailedDesc: "请确保您的图谱运行在 {url}，并且 API 密钥设置正确（如果连接到已部署的图谱）。",
    invalidInput: "输入无效",
    networkError: "网络错误",
    unknownError: "未知错误",
  },

  // GitHub 链接
  github: {
    openRepo: "打开 GitHub 仓库",
  },
};

export type Translations = typeof zhCN;

