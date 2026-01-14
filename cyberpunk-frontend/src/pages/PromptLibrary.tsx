import React, { useState } from 'react';
import { Button } from 'antd';
import { Sparkles, Terminal, Bug, FileText, Code, Search, Copy } from 'lucide-react';
import { motion } from 'framer-motion';
import { CyberCard } from '../components/CyberCard';

interface PromptTemplate {
  id: string;
  title: string;
  description: string;
  content: string;
  tags: string[];
  category: 'Testing' | 'Debugging' | 'Documentation';
}

const mockTemplates: PromptTemplate[] = [
  {
    id: '1',
    title: '生成冒烟测试',
    description: '为关键用户路径创建全面的冒烟测试套件。',
    content: '分析以下 API 端点并使用 Jest/Supertest 生成冒烟测试套件。专注于用户登录和结账流程的"快乐路径"...',
    tags: ['Jest', 'API 测试'],
    category: 'Testing'
  },
  {
    id: '2',
    title: '解释复杂正则表达式',
    description: '将复杂的正则表达式分解为通俗易懂的语言。',
    content: '详细解释以下正则表达式。分解每个捕获组和逻辑标记：\n\n/^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{8,}$/',
    tags: ['正则表达式', '教育'],
    category: 'Debugging'
  },
  {
    id: '3',
    title: '生成 API 文档',
    description: '将代码或原始路由定义转换为 Swagger/OpenAPI 规范。',
    content: '获取以下 Express.js 路由定义并生成 YAML 格式的 OpenAPI 3.0 规范。包含请求参数和示例响应...',
    tags: ['Swagger', 'OpenAPI'],
    category: 'Documentation'
  },
  {
    id: '4',
    title: 'React 组件单元测试',
    description: '为 UI 组件生成 React Testing Library 测试。',
    content: '使用 React Testing Library 为以下 React 组件编写单元测试。确保用户交互（点击、输入）100% 覆盖率...',
    tags: ['React', 'RTL'],
    category: 'Testing'
  },
  {
    id: '5',
    title: 'SQL 查询优化器',
    description: '分析 SQL 查询并建议性能改进。',
    content: '分析提供的 SQL 查询的性能瓶颈。建议适当的索引并重写查询以优化执行时间...',
    tags: ['SQL', '性能'],
    category: 'Debugging'
  },
  {
    id: '6',
    title: 'Git 提交消息生成器',
    description: '从差异生成语义提交消息。',
    content: '基于以下 `git diff` 输出，生成符合 Conventional Commits 的提交消息。保持主题在 50 个字符以内...',
    tags: ['Git', '工作流'],
    category: 'Documentation'
  },
  {
    id: '7',
    title: '生成测试数据',
    description: '为应用程序生成测试数据。',
    content: '生成测试数据以模拟真实世界的场景。确保数据的多样性和覆盖率...',
    tags: ['测试数据', '模拟'],
    category: 'Testing'
  },
  {
    id: '8',
    title: '调试 Node.js 应用程序',
    description: '使用 Node.js 内置调试工具调试应用程序。',
    content: '使用 Node.js 内置调试工具调试应用程序。设置断点、检查变量和调用栈...',
    tags: ['Node.js', '调试'],
    category: 'Debugging'
  },
  {
    id: '9',
    title: '生成文档',
    description: '为应用程序生成文档。',
    content: '生成文档以帮助用户理解应用程序的功能和使用方法。包括 API 文档、用户手册和教程...',
    tags: ['文档', '帮助'],
    category: 'Documentation'
  }
];

const categories = ['All', 'Testing', 'Debugging', 'Documentation'];

export const PromptLibrary: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredTemplates = mockTemplates.filter(template => {
    const matchesCategory = activeCategory === 'All' || template.category === activeCategory;
    const matchesSearch = template.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          template.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Testing': return <Terminal size={14} />;
      case 'Debugging': return <Bug size={14} />;
      case 'Documentation': return <FileText size={14} />;
      default: return <Code size={14} />;
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <motion.div 
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-bold font-display text-white mb-1 drop-shadow-md">Prompt Library</h1>
          <p className="text-slate-400 font-mono text-sm">Manage and reuse your AI instruction templates</p>
        </motion.div>
        <motion.div 
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="flex items-center gap-3"
        >
           <Button type="primary" icon={<Sparkles size={16} />} className="cyber-button">
             Create Template
           </Button>
        </motion.div>
      </div>

      {/* Search and Filters */}
      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex flex-col sm:flex-row gap-4 p-1"
      >
        <div className="relative flex-1 group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-neon-cyan transition-colors" size={16} />
          <input 
            type="text" 
            placeholder="Search templates..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-900/50 border border-slate-700 rounded-lg pl-10 pr-4 py-3 text-sm text-slate-200 focus:outline-none focus:border-neon-cyan focus:ring-1 focus:ring-neon-cyan/50 transition-all placeholder:text-slate-600"
          />
        </div>
        <div className="flex gap-2 overflow-x-auto pb-2 sm:pb-0 custom-scrollbar">
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setActiveCategory(category)}
              className={`px-6 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                activeCategory === category
                  ? 'bg-neon-cyan text-black shadow-[0_0_15px_rgba(0,243,255,0.4)] font-bold'
                  : 'bg-slate-900/50 text-slate-400 hover:text-white border border-slate-700 hover:border-slate-500'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTemplates.map((template, index) => (
          <CyberCard 
            key={template.id} 
            className="!p-5 h-full flex flex-col hover:scale-[1.02] transition-transform duration-300"
            delay={0.1 * index}
          >
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center gap-2 text-xs font-medium px-2 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-slate-300 font-mono">
                {getCategoryIcon(template.category)}
                {template.category}
              </div>
              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button type="text" size="small" icon={<Copy size={14} />} className="text-slate-400! hover:text-white!" />
              </div>
            </div>

            <h3 className="text-lg font-bold text-white mb-2 group-hover:text-neon-cyan transition-colors font-display tracking-wide">
              {template.title}
            </h3>
            <p className="text-slate-400 text-sm mb-4 line-clamp-2">
              {template.description}
            </p>

            <div className="bg-slate-950/80 rounded-lg p-3 mb-4 border border-slate-800 flex-1 relative overflow-hidden group/code">
              <code className="text-xs text-slate-300 font-mono block line-clamp-4 leading-relaxed">
                {template.content}
              </code>
              <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-slate-950/90 pointer-events-none" />
            </div>

            <div className="flex items-center justify-between mt-auto pt-4 border-t border-slate-800/50">
              <div className="flex gap-2">
                {template.tags.map(tag => (
                  <span key={tag} className="text-[10px] text-slate-500 bg-slate-800/30 px-2 py-1 rounded border border-slate-800/50 font-mono">
                    #{tag}
                  </span>
                ))}
              </div>
              <Button 
                size="small" 
                className="bg-neon-cyan/10! text-neon-cyan! border-neon-cyan/20! hover:bg-neon-cyan! hover:text-white! hover:border-neon-cyan! transition-all flex items-center gap-1.5 font-bold tracking-wide"
              >
                <Sparkles size={14} />
                USE
              </Button>
            </div>
          </CyberCard>
        ))}
      </div>
    </motion.div>
  );
};


