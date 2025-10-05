// Copyright (c) 2025 左岚. All rights reserved.
/**
 * Markdown 渲染工具
 */

/**
 * 简单的 Markdown 转 HTML 渲染器
 * 支持常见的 Markdown 语法
 */
export function renderMarkdown(text: string): string {
  if (!text) return ''
  
  let html = text
  
  // 代码块 (```language\ncode\n```)
  html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
    const language = lang || 'text'
    return `<pre class="code-block"><code class="language-${language}">${escapeHtml(code.trim())}</code></pre>`
  })
  
  // 行内代码 (`code`)
  html = html.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
  
  // 标题 (# H1, ## H2, etc.)
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>')
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>')
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>')
  
  // 粗体 (**text** or __text__)
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/__(.+?)__/g, '<strong>$1</strong>')
  
  // 斜体 (*text* or _text_)
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  html = html.replace(/_(.+?)_/g, '<em>$1</em>')
  
  // 删除线 (~~text~~)
  html = html.replace(/~~(.+?)~~/g, '<del>$1</del>')
  
  // 链接 [text](url)
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
  
  // 图片 ![alt](url)
  html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" />')
  
  // 无序列表 (- item or * item)
  html = html.replace(/^\s*[-*]\s+(.+)$/gim, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
  
  // 有序列表 (1. item)
  html = html.replace(/^\s*\d+\.\s+(.+)$/gim, '<li>$1</li>')
  
  // 引用 (> text)
  html = html.replace(/^>\s+(.+)$/gim, '<blockquote>$1</blockquote>')
  
  // 分隔线 (--- or ***)
  html = html.replace(/^---$/gim, '<hr />')
  html = html.replace(/^\*\*\*$/gim, '<hr />')
  
  // 段落 (双换行符)
  html = html.replace(/\n\n/g, '</p><p>')
  html = `<p>${html}</p>`
  
  // 单换行符转 <br>
  html = html.replace(/\n/g, '<br />')
  
  // 清理空段落
  html = html.replace(/<p><\/p>/g, '')
  html = html.replace(/<p>\s*<\/p>/g, '')
  
  return html
}

/**
 * 转义 HTML 特殊字符
 */
function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  }
  return text.replace(/[&<>"']/g, (char) => map[char])
}

/**
 * 代码高亮 (简单实现)
 */
export function highlightCode(code: string, language: string): string {
  // 这是一个简化版本,实际项目中建议使用 highlight.js 或 prism.js
  const keywords: Record<string, string[]> = {
    javascript: ['const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 'while', 'class', 'import', 'export'],
    typescript: ['const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 'while', 'class', 'import', 'export', 'interface', 'type'],
    python: ['def', 'class', 'import', 'from', 'return', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'with', 'as'],
    java: ['public', 'private', 'protected', 'class', 'interface', 'void', 'return', 'if', 'else', 'for', 'while', 'try', 'catch'],
  }
  
  let highlighted = escapeHtml(code)
  
  // 高亮关键字
  const langKeywords = keywords[language.toLowerCase()] || []
  langKeywords.forEach(keyword => {
    const regex = new RegExp(`\\b${keyword}\\b`, 'g')
    highlighted = highlighted.replace(regex, `<span class="keyword">${keyword}</span>`)
  })
  
  // 高亮字符串
  highlighted = highlighted.replace(/(["'])(?:(?=(\\?))\2.)*?\1/g, '<span class="string">$&</span>')
  
  // 高亮注释
  highlighted = highlighted.replace(/\/\/.*/g, '<span class="comment">$&</span>')
  highlighted = highlighted.replace(/\/\*[\s\S]*?\*\//g, '<span class="comment">$&</span>')
  
  // 高亮数字
  highlighted = highlighted.replace(/\b\d+\b/g, '<span class="number">$&</span>')
  
  return highlighted
}

/**
 * 从文本中提取代码块
 */
export function extractCodeBlocks(text: string): Array<{ language: string; code: string }> {
  const blocks: Array<{ language: string; code: string }> = []
  const regex = /```(\w+)?\n([\s\S]*?)```/g
  let match
  
  while ((match = regex.exec(text)) !== null) {
    blocks.push({
      language: match[1] || 'text',
      code: match[2].trim()
    })
  }
  
  return blocks
}

/**
 * 复制代码到剪贴板
 */
export async function copyCode(code: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(code)
    return true
  } catch (error) {
    console.error('复制失败:', error)
    return false
  }
}


