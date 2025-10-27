// 国际化上下文
"use client";

import React, { createContext, useContext, ReactNode, useState } from "react";
import { zhCN, en, Translations } from "@/locales";

// 支持的语言类型
type Language = "zh-CN" | "en";

// 国际化上下文类型
interface I18nContextType {
  language: Language; // 当前语言
  setLanguage: (lang: Language) => void; // 切换语言
  t: (key: string, params?: Record<string, string | number>) => string; // 翻译函数
  translations: Translations; // 当前语言的翻译对象
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

// 语言包映射
const translationsMap: Record<Language, Translations> = {
  "zh-CN": zhCN,
  en: en,
};

// 从嵌套对象中获取值的辅助函数
function getNestedValue(obj: any, path: string): string {
  const keys = path.split(".");
  let result = obj;

  for (const key of keys) {
    if (result && typeof result === "object" && key in result) {
      result = result[key];
    } else {
      return path; // 如果找不到，返回原始 key
    }
  }

  return typeof result === "string" ? result : path;
}

// 替换字符串中的占位符，如 {count} -> 3
function replacePlaceholders(
  text: string,
  params?: Record<string, string | number>,
): string {
  if (!params) return text;

  let result = text;
  Object.entries(params).forEach(([key, value]) => {
    result = result.replace(new RegExp(`\\{${key}\\}`, "g"), String(value));
  });

  return result;
}

export function I18nProvider({ children }: { children: ReactNode }) {
  // 默认使用中文
  const [language, setLanguage] = useState<Language>("zh-CN");

  // 翻译函数
  const t = (key: string, params?: Record<string, string | number>): string => {
    const translations = translationsMap[language];
    const text = getNestedValue(translations, key);
    return replacePlaceholders(text, params);
  };

  const value = {
    language,
    setLanguage,
    t,
    translations: translationsMap[language],
  };

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

// 自定义 Hook
export function useI18n() {
  const context = useContext(I18nContext);
  if (context === undefined) {
    throw new Error("useI18n 必须在 I18nProvider 内部使用");
  }
  return context;
}

