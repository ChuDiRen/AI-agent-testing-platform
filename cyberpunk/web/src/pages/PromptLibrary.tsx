import React, { useState } from 'react';
import { Button } from 'antd';
import { Sparkles, Terminal, Bug, FileText, Code, Search } from 'lucide-react';
import { motion } from 'framer-motion';
import { Card, CardContent } from '../components/ui/Card';

interface PromptTemplate {
  id: string;
  title: string;
  description: string;
  content: string;
  tags: string[];
  category: '测试' | '调试' | '文档';
}

const mockTemplates: PromptTemplate[] = [
  {
    id: '1',
    title: '生成冒烟测试',
    description: '为关键用户路径创建全面的冒烟测试套件。',
    content: '分析以下 API 端点并使用 Jest/Supertest 生成冒烟测试套件。专注于用户登录和结账的“快乐路径”...',
    tags: ['Jest', 'API 测试'],
    category: '测试'
  },
  {
    id: '2',
    title: '解释复杂正则',
    description: '将复杂的正则表达式分解为通俗易懂的语言。',
    content: '详细解释以下正则表达式。分解每个捕获组和逻辑标记：\n\n/^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{8,}$/',
    tags: ['正则', '教育'],
    category: '调试'
  },
  {
    id: '3',
    title: '生成 API 文档',
    description: '将代码或原始路由定义转换为 Swagger/OpenAPI 规范。',
    content: '获取以下 Express.js 路由定义并生成 YAML 格式的 OpenAPI 3.0 规范。包括参数和示例响应...',
    tags: ['Swagger', 'OpenAPI'],
    category: '文档'
  },
  {
    id: '4',
    title: 'React 单元测试',
    description: '为 UI 组件生成 React Testing Library 测试。',
    content: '使用 React Testing Library 为以下 React 组件编写单元测试。确保用户交互（点击、输入）的 100% 覆盖率...',
    tags: ['React', 'RTL'],
    category: '测试'
  },
  {
    id: '5',
    title: 'SQL 查询优化器',
    description: '分析 SQL 查询并建议性能改进。',
    content: '分析所提供 SQL 查询的性能瓶颈。建议适当的索引并重写查询以优化执行时间...',
    tags: ['SQL', '性能'],
    category: '调试'
  },
  {
    id: '6',
    title: '提交信息生成器',
    description: '从 diff 生成语义化提交信息。',
    content: '根据以下 `git diff` 输出，生成遵循 Conventional Commits 的提交信息。保持主题在 50 个字符以内...',
    tags: ['Git', '工作流'],
    category: '文档'
  },
  {
    id: '7',
    title: '生成测试数据',
    description: '生成用于应用程序种子的测试数据。',
    content: '生成测试数据以模拟真实场景。确保多样性和边缘情况覆盖...',
    tags: ['数据', 'Mock'],
    category: '测试'
  },
  {
    id: '8',
    title: '调试 Node.js 应用',
    description: '使用 Node.js 内置工具调试应用程序。',
    content: '使用 Node.js 内置调试器调试应用程序。设置断点，检查变量和调用堆栈...',
    tags: ['Node.js', '调试'],
    category: '调试'
  },
  {
    id: '9',
    title: '生成文档',
    description: '为应用程序生成用户文档。',
    content: '生成文档以帮助用户了解应用程序功能和用法。包括 API 文档、用户手册和教程...',
    tags: ['文档', '帮助'],
    category: '文档'
  }
];

const categories = ['全部', '测试', '调试', '文档'];

export const PromptLibrary: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState('全部');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredTemplates = mockTemplates.filter(template => {
    const matchesCategory = activeCategory === '全部' || template.category === activeCategory;
    const matchesSearch = template.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case '测试': return <Terminal size={14} />;
      case '调试': return <Bug size={14} />;
      case '文档': return <FileText size={14} />;
      default: return <Code size={14} />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6 max-w-7xl mx-auto"
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">提示词库</h1>
          <p className="text-slate-500 text-sm">管理和复用您的 AI 指令模板</p>
        </div>
        <div className="flex items-center gap-3">
          <Button type="primary" icon={<Sparkles size={16} />} className="bg-primary hover:bg-blue-700 h-9">
            创建模板
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4 p-1">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input
            type="text"
            placeholder="搜索模板..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white border border-slate-200 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-700 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition-all placeholder:text-slate-400 shadow-sm"
          />
        </div>
        <div className="flex gap-2 overflow-x-auto pb-2 sm:pb-0">
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setActiveCategory(category)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${activeCategory === category
                ? 'bg-slate-900 text-white shadow-sm'
                : 'bg-white text-slate-600 hover:text-slate-900 border border-slate-200 hover:border-slate-300'
                }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTemplates.map((template) => (
          <Card
            key={template.id}
            className="h-full flex flex-col hover:shadow-md transition-shadow duration-300 cursor-pointer group"
          >
            <CardContent className="p-5 flex flex-col h-full">
              <div className="flex justify-between items-start mb-3">
                <div className="flex items-center gap-2 text-xs font-medium px-2 py-1 rounded-full bg-slate-100 border border-slate-200 text-slate-600">
                  {getCategoryIcon(template.category)}
                  {template.category}
                </div>
              </div>

              <h3 className="text-lg font-bold text-slate-900 mb-2 group-hover:text-primary transition-colors">
                {template.title}
              </h3>
              <p className="text-slate-500 text-sm mb-4 line-clamp-2">
                {template.description}
              </p>

              <div className="bg-slate-50 rounded-lg p-3 mb-4 border border-slate-100 flex-1 relative overflow-hidden">
                <code className="text-xs text-slate-600 font-mono block line-clamp-3 leading-relaxed">
                  {template.content}
                </code>
              </div>

              <div className="flex items-center justify-between mt-auto pt-4 border-t border-slate-100">
                <div className="flex gap-2">
                  {template.tags.slice(0, 2).map(tag => (
                    <span key={tag} className="text-[10px] text-slate-500 bg-slate-100 px-2 py-1 rounded border border-slate-200">
                      #{tag}
                    </span>
                  ))}
                </div>
                <Button
                  size="small"
                  type="text"
                  className="text-primary hover:text-blue-700 hover:bg-blue-50 font-medium flex items-center gap-1.5"
                >
                  <Sparkles size={14} />
                  使用
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </motion.div>
  );
};
