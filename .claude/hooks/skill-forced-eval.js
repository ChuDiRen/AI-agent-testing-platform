#!/usr/bin/env node
/**
 * Skill Forced Evaluation Hook（核心钩子 v2.0）
 * 用户提交问题时触发，强制评估所有技能并激活相关技能
 * 
 * 升级内容：
 * 1. 支持多技能组合激活
 * 2. 支持 SubAgent 推荐
 * 3. 支持 Command 联动提示
 */

const fs = require('fs');
const path = require('path');

// 技能定义列表（共36个技能）
const skills = [
  // ========== 后端开发 (6个) ==========
  { name: 'crud-development', keywords: ['CRUD', '增删改查', '列表', '详情', '新增', '编辑', '删除', 'Controller', 'Service', '业务模块'], category: '后端开发' },
  { name: 'api-development', keywords: ['API', '接口', 'FastAPI', '端点', 'router', '路由', 'RESTful', 'Endpoint'], category: '后端开发' },
  { name: 'api-documentation', keywords: ['API文档', '接口文档', 'Swagger', 'OpenAPI', '文档生成'], category: '后端开发' },
  { name: 'database-design', keywords: ['数据库', 'SQL', '建表', 'MySQL', '字典', 'DDL', '索引', '迁移', 'schema', '数据库设计', '表结构'], category: '后端开发' },
  { name: 'backend-annotations', keywords: ['注解', '装饰器', 'Depends', 'Decorator', '依赖注入'], category: '后端开发' },
  { name: 'error-handler', keywords: ['异常', '错误', 'Exception', 'try-catch', '错误处理', '异常处理'], category: '后端开发' },
  
  // ========== 前端开发 (3个) ==========
  { name: 'ui-pc', keywords: ['PC端', '管理后台', 'Element', '表格', '表单', 'Vue', '页面', 'List', 'Form', '弹窗', 'Modal', 'Dialog'], category: '前端开发' },
  { name: 'store-management', keywords: ['Vuex', 'Pinia', '状态管理', 'store', 'state', '全局状态'], category: '前端开发' },
  { name: 'prototype-design', keywords: ['原型', '原型设计', 'UI设计', '界面设计', '交互设计', 'Figma'], category: '前端开发' },
  
  // ========== 移动端 (3个) ==========
  { name: 'ui-mobile', keywords: ['移动端', 'H5', '小程序', 'Vant', '手机', 'mobile', 'rem', 'vw', '适配', '响应式'], category: '移动端' },
  { name: 'store-mobile', keywords: ['移动端状态', 'uni-app store', '小程序状态'], category: '移动端' },
  { name: 'uniapp-platform', keywords: ['uni-app', '条件编译', '跨平台', '多端', '#ifdef'], category: '移动端' },
  
  // ========== 业务集成 (4个) ==========
  { name: 'payment-integration', keywords: ['支付', '微信支付', '支付宝', '订单支付', 'Payment'], category: '业务集成' },
  { name: 'wechat-integration', keywords: ['微信', '公众号', '小程序登录', '分享', 'JSSDK'], category: '业务集成' },
  { name: 'file-oss-management', keywords: ['文件上传', 'OSS', '对象存储', '图片上传', '文件管理', 'MinIO'], category: '业务集成' },
  { name: 'ai-langchain4j', keywords: ['AI', '大模型', 'LLM', 'ChatGPT', 'Claude', 'LangChain', 'LangGraph', 'RAG'], category: '业务集成' },
  
  // ========== AI 开发 (2个) ==========
  { name: 'ai-agent', keywords: ['Agent', '智能体', 'AI Agent', '代理', '自动化'], category: 'AI开发' },
  { name: 'ai-prompt', keywords: ['Prompt', '提示词', '提示工程', 'Prompt Engineering'], category: 'AI开发' },
  
  // ========== 质量保障 (4个) ==========
  { name: 'bug-detective', keywords: ['Bug', '问题', '排查', '调试', 'debug', '故障'], category: '质量保障' },
  { name: 'performance', keywords: ['性能', '优化', '缓存', '慢查询', '响应时间', '并发'], category: '质量保障' },
  { name: 'security-guard', keywords: ['安全', 'XSS', 'SQL注入', '权限', '认证', '加密', 'CSRF'], category: '质量保障' },
  { name: 'code-patterns', keywords: ['设计模式', '代码规范', '重构', '命名', '最佳实践'], category: '质量保障' },
  
  // ========== 测试 (4个) ==========
  { name: 'api-testing', keywords: ['接口测试', 'API测试', 'httpx', 'pytest', '自动化测试'], category: '测试' },
  { name: 'unit-testing', keywords: ['单元测试', 'unittest', 'pytest', 'mock', '测试用例'], category: '测试' },
  { name: 'webapp-testing', keywords: ['Web测试', 'E2E测试', 'Playwright', '端到端测试', '浏览器测试'], category: '测试' },
  { name: 'code-review', keywords: ['代码审查', 'Code Review', 'PR审查', '代码评审'], category: '测试' },
  
  // ========== 工程管理 (6个) ==========
  { name: 'architecture-design', keywords: ['架构', '设计', '分层', '模块化', '微服务', '系统设计'], category: '工程管理' },
  { name: 'project-navigator', keywords: ['项目结构', '目录', '文件在哪', '代码在哪', '结构'], category: '工程管理' },
  { name: 'git-workflow', keywords: ['Git', '分支', '提交', 'PR', 'merge', 'rebase', 'commit'], category: '工程管理' },
  { name: 'tech-decision', keywords: ['技术选型', '选择', '对比', '用哪个', '推荐'], category: '工程管理' },
  { name: 'brainstorm', keywords: ['头脑风暴', '想法', '方案', '怎么做', '建议', '思路'], category: '工程管理' },
  { name: 'task-splitting', keywords: ['任务拆分', '需求拆分', '任务分解', '工作分解'], category: '工程管理' },
  
  // ========== DevOps (3个) ==========
  { name: 'ci-cd', keywords: ['CI/CD', '持续集成', '持续部署', 'Jenkins', 'GitHub Actions', '流水线'], category: 'DevOps' },
  { name: 'docker-deploy', keywords: ['Docker', '容器', '部署', 'Dockerfile', 'docker-compose', 'K8s'], category: 'DevOps' },
  { name: 'logging-monitor', keywords: ['日志', '监控', '告警', 'ELK', 'Prometheus', 'Grafana'], category: 'DevOps' },
  
  // ========== 工具 (1个) ==========
  { name: 'skill-creator', keywords: ['创建技能', '新技能', 'Skill', '技能开发'], category: '工具' }
];

// SubAgent 推荐规则
const agentRecommendations = {
  '安全': { agent: 'security-auditor', reason: '深度安全审计' },
  'SQL注入': { agent: 'security-auditor', reason: '安全漏洞分析' },
  'XSS': { agent: 'security-auditor', reason: '安全漏洞分析' },
  '代码审查': { agent: 'code-reviewer', reason: '代码质量审查' },
  'Code Review': { agent: 'code-reviewer', reason: '代码质量审查' },
  'PR审查': { agent: 'code-reviewer', reason: 'PR 代码审查' },
  'Bug': { agent: 'debugger', reason: 'Bug 排查定位' },
  '排查': { agent: 'debugger', reason: '问题排查' },
  '调试': { agent: 'debugger', reason: '调试分析' },
  '前端': { agent: 'frontend-developer', reason: 'Vue3 组件开发' },
  'Vue': { agent: 'frontend-developer', reason: 'Vue3 组件开发' },
  'Element': { agent: 'frontend-developer', reason: 'Element Plus 组件' },
  '后端': { agent: 'backend-architect', reason: 'FastAPI 架构设计' },
  'FastAPI': { agent: 'backend-architect', reason: 'FastAPI 开发' },
  '数据库': { agent: 'database-architect', reason: '数据库设计' },
  '建表': { agent: 'database-architect', reason: '表结构设计' },
  '测试': { agent: 'test-engineer', reason: '测试用例设计' }
};

// Command 联动规则
const commandRecommendations = {
  'CRUD': '/crud',
  '增删改查': '/crud',
  '代码检查': '/check',
  '规范检查': '/check',
  '安全检查': '/security',
  '性能分析': '/perf',
  '部署': '/deploy',
  'Docker': '/deploy docker',
  '代码审查': '/review',
  'Code Review': '/review'
};

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

// 推荐 SubAgent
function recommendAgent(userPrompt) {
  for (const [keyword, recommendation] of Object.entries(agentRecommendations)) {
    if (userPrompt.includes(keyword)) {
      return recommendation;
    }
  }
  return null;
}

// 推荐 Command
function recommendCommand(userPrompt) {
  for (const [keyword, command] of Object.entries(commandRecommendations)) {
    if (userPrompt.includes(keyword)) {
      return { keyword, command };
    }
  }
  return null;
}

// 从 stdin 读取数据
async function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    
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
    
    if (stdinData.trim()) {
      try {
        const inputData = JSON.parse(stdinData);
        prompt = inputData.prompt || inputData.user_prompt || '';
      } catch {
        prompt = stdinData;
      }
    }
    
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
    const agentRec = recommendAgent(prompt);
    const commandRec = recommendCommand(prompt);
    
    const outputs = [];
    
    // 技能激活
    if (matchedSkills.length > 0) {
      const skillNames = matchedSkills.map(s => s.name).join(', ');
      const skillFiles = matchedSkills.map(s => `- .claude/skills/${s.name}/SKILL.md`).join('\n');
      outputs.push(`[技能激活] 检测到 ${matchedSkills.length} 个相关技能：${skillNames}\n请读取以下技能文件获取规范：\n${skillFiles}`);
    }
    
    // SubAgent 推荐
    if (agentRec) {
      outputs.push(`[Agent推荐] 可使用 /agent ${agentRec.agent} 进行${agentRec.reason}（独立上下文，深度分析）`);
    }
    
    // Command 推荐
    if (commandRec) {
      outputs.push(`[命令提示] 可使用 ${commandRec.command} 命令快速执行`);
    }
    
    if (outputs.length > 0) {
      console.log(outputs.join('\n\n'));
    }
    
    process.exit(0);
  } catch (error) {
    process.exit(0);
  }
}

main();
