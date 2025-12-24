#!/usr/bin/env node
/**
 * Skill Forced Evaluation Hook（核心钩子）
 * 用户提交问题时触发，强制评估所有技能并激活相关技能
 * Claude Code 通过 stdin 传递 JSON 数据
 */

const fs = require('fs');
const path = require('path');

// 技能定义列表
const skills = [
  // ========== 后端开发 ==========
  { name: 'crud-development', keywords: ['CRUD', '增删改查', '列表', '详情', '新增', '编辑', '删除', 'Controller', 'Service', '业务模块'], category: '后端开发' },
  { name: 'api-development', keywords: ['API', '接口', 'FastAPI', '端点', 'router', '路由', 'RESTful', 'Endpoint'], category: '后端开发' },
  { name: 'database-ops', keywords: ['数据库', 'SQL', '建表', 'MySQL', '字典', 'DDL', '索引', '迁移', 'schema'], category: '后端开发' },
  { name: 'backend-annotations', keywords: ['注解', '装饰器', 'Depends', 'Decorator', '依赖注入'], category: '后端开发' },
  { name: 'error-handler', keywords: ['异常', '错误', 'Exception', 'try-catch', '错误处理', '异常处理'], category: '后端开发' },
  
  // ========== 前端开发 ==========
  { name: 'ui-pc', keywords: ['PC端', '管理后台', 'Element', '表格', '表单', 'Vue', '页面', 'List', 'Form', '弹窗', 'Modal', 'Dialog'], category: '前端开发' },
  { name: 'store-pc', keywords: ['Vuex', 'Pinia', '状态管理', 'store', 'state', '全局状态'], category: '前端开发' },
  
  // ========== 移动端 ==========
  { name: 'ui-mobile', keywords: ['移动端', 'H5', '小程序', 'Vant', '手机', 'mobile'], category: '移动端' },
  { name: 'ui-design-mobile', keywords: ['移动端设计', 'rem', 'vw', '适配', '响应式', '安全区域'], category: '移动端' },
  { name: 'store-mobile', keywords: ['移动端状态', 'uni-app store', '小程序状态'], category: '移动端' },
  { name: 'uniapp-platform', keywords: ['uni-app', '条件编译', '跨平台', '多端', '#ifdef'], category: '移动端' },
  
  // ========== 业务集成 ==========
  { name: 'payment-integration', keywords: ['支付', '微信支付', '支付宝', '订单支付', 'Payment'], category: '业务集成' },
  { name: 'wechat-integration', keywords: ['微信', '公众号', '小程序登录', '分享', 'JSSDK'], category: '业务集成' },
  { name: 'file-oss-management', keywords: ['文件上传', 'OSS', '对象存储', '图片上传', '文件管理', 'MinIO'], category: '业务集成' },
  { name: 'ai-langchain4j', keywords: ['AI', '大模型', 'LLM', 'ChatGPT', 'Claude', 'LangChain', 'LangGraph', 'RAG'], category: '业务集成' },
  
  // ========== 质量保障 ==========
  { name: 'bug-detective', keywords: ['Bug', '问题', '排查', '调试', 'debug', '故障'], category: '质量保障' },
  { name: 'performance-doctor', keywords: ['性能', '优化', '缓存', '慢查询', '响应时间', '并发'], category: '质量保障' },
  { name: 'security-guard', keywords: ['安全', 'XSS', 'SQL注入', '权限', '认证', '加密', 'CSRF'], category: '质量保障' },
  { name: 'code-patterns', keywords: ['设计模式', '代码规范', '重构', '命名', '最佳实践'], category: '质量保障' },
  
  // ========== 工程管理 ==========
  { name: 'architecture-design', keywords: ['架构', '设计', '分层', '模块化', '微服务', '系统设计'], category: '工程管理' },
  { name: 'project-navigator', keywords: ['项目结构', '目录', '文件在哪', '代码在哪', '结构'], category: '工程管理' },
  { name: 'git-workflow', keywords: ['Git', '分支', '提交', 'PR', 'merge', 'rebase', 'commit'], category: '工程管理' },
  { name: 'tech-decision', keywords: ['技术选型', '选择', '对比', '用哪个', '推荐'], category: '工程管理' },
  { name: 'brainstorm', keywords: ['头脑风暴', '想法', '方案', '怎么做', '建议', '思路'], category: '工程管理' }
];

// 评估技能相关性
function evaluateSkills(userPrompt) {
  if (!userPrompt) return [];
  const lowerPrompt = userPrompt.toLowerCase();
  const matchedSkills = [];
  
  for (const skill of skills) {
    const isMatch = skill.keywords.some(keyword => 
      lowerPrompt.includes(keyword.toLowerCase())
    );
    if (isMatch) {
      matchedSkills.push(skill);
    }
  }
  
  return matchedSkills;
}

// 从 stdin 读取数据
async function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    
    // 设置超时，如果没有输入则使用空数据
    const timeout = setTimeout(() => {
      resolve(data);
    }, 100);
    
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => {
      clearTimeout(timeout);
      data += chunk;
    });
    process.stdin.on('end', () => {
      clearTimeout(timeout);
      resolve(data);
    });
    process.stdin.on('error', () => {
      clearTimeout(timeout);
      resolve(data);
    });
    
    // 如果 stdin 不是 TTY，开始读取
    if (!process.stdin.isTTY) {
      process.stdin.resume();
    } else {
      clearTimeout(timeout);
      resolve('');
    }
  });
}

// 主函数
async function main() {
  try {
    const stdinData = await readStdin();
    let prompt = '';
    
    // 尝试解析 JSON
    if (stdinData.trim()) {
      try {
        const inputData = JSON.parse(stdinData);
        prompt = inputData.prompt || inputData.user_prompt || '';
      } catch {
        // 如果不是 JSON，直接使用原始数据
        prompt = stdinData;
      }
    }
    
    // 也检查命令行参数
    if (!prompt && process.argv.length > 2) {
      prompt = process.argv.slice(2).join(' ');
    }
    
    if (!prompt.trim()) {
      process.exit(0);
    }
    
    // 检测是否为斜杠命令
    if (/^\/[^\/\s]+/.test(prompt.trim())) {
      process.exit(0);
    }
    
    const matchedSkills = evaluateSkills(prompt);
    
    if (matchedSkills.length > 0) {
      // 输出上下文信息，Claude 会看到这些内容
      const context = `[技能激活] 检测到 ${matchedSkills.length} 个相关技能：${matchedSkills.map(s => s.name).join(', ')}
请读取以下技能文件获取规范：
${matchedSkills.map(s => `- .claude/skills/${s.name}/SKILL.md`).join('\n')}`;
      
      console.log(context);
    }
    
    process.exit(0);
  } catch (error) {
    // 静默失败，不阻塞用户操作
    process.exit(0);
  }
}

main();
