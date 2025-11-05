import { getLangSmithApiKey } from './config';

export function getApiKey(): string | null {
  try {
    if (typeof window === "undefined") return null;
    
    // 优先从配置中读取
    const configApiKey = getLangSmithApiKey();
    if (configApiKey) return configApiKey;
    
    // 兼容旧的 localStorage 存储
    return window.localStorage.getItem("lg:chat:apiKey") ?? null;
  } catch {
    // no-op
  }

  return null;
}
