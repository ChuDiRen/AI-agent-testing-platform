/**
 * Agent Chat 配置管理
 * 从 window.AGENT_CHAT_CONFIG 或 localStorage 读取配置
 */

export interface AgentChatConfig {
  NEXT_PUBLIC_API_URL: string;
  NEXT_PUBLIC_ASSISTANT_ID: string;
  LANGSMITH_API_KEY?: string;
}

// 从环境变量读取默认配置，默认使用后端FastAPI的LangGraph兼容API
const DEFAULT_CONFIG: AgentChatConfig = {
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/langgraph',
  NEXT_PUBLIC_ASSISTANT_ID: process.env.NEXT_PUBLIC_ASSISTANT_ID || 'testcase',
  LANGSMITH_API_KEY: undefined,
};

/**
 * 获取配置
 */
export function getAgentConfig(): AgentChatConfig {
  // 1. 优先从 window 对象读取（Vue 组件设置）
  if (typeof window !== 'undefined' && (window as any).AGENT_CHAT_CONFIG) {
    return (window as any).AGENT_CHAT_CONFIG;
  }

  // 2. 从 localStorage 读取
  if (typeof window !== 'undefined') {
    try {
      const savedConfig = localStorage.getItem('agent-chat-config');
      if (savedConfig) {
        const parsed = JSON.parse(savedConfig);
        return {
          NEXT_PUBLIC_API_URL: parsed.deploymentUrl || DEFAULT_CONFIG.NEXT_PUBLIC_API_URL,
          NEXT_PUBLIC_ASSISTANT_ID: parsed.assistantId || DEFAULT_CONFIG.NEXT_PUBLIC_ASSISTANT_ID,
          LANGSMITH_API_KEY: parsed.langsmithApiKey || undefined,
        };
      }
    } catch (error) {
      console.error('读取配置失败:', error);
    }
  }

  // 3. 返回默认配置
  return DEFAULT_CONFIG;
}

/**
 * 获取 API URL
 */
export function getApiUrl(): string {
  const config = getAgentConfig();
  return config.NEXT_PUBLIC_API_URL;
}

/**
 * 获取 Assistant ID
 */
export function getAssistantId(): string {
  const config = getAgentConfig();
  return config.NEXT_PUBLIC_ASSISTANT_ID;
}

/**
 * 获取 LangSmith API Key
 */
export function getLangSmithApiKey(): string | undefined {
  const config = getAgentConfig();
  return config.LANGSMITH_API_KEY;
}

