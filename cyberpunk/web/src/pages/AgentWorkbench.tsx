import React, { useState } from 'react';
import type { CSSProperties } from 'react';
import { Button, Input, Tabs, Avatar, Tooltip } from 'antd';
import {
  Plus,
  MessageSquare,
  MoreHorizontal,
  Paperclip,
  Send,
  Code,
  FileText,
  Play,
  Copy,
  Check,
  Bot
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { motion } from 'framer-motion';

// --- Mock Data ---

const chatHistory = [
  {
    group: '今天',
    items: [
      { id: '1', title: '重构认证模块', time: '10:30 AM', active: true },
      { id: '2', title: '调试 API 延迟', time: '9:15 AM', active: false },
    ]
  },
  {
    group: '昨天',
    items: [
      { id: '3', title: '新特性：深色模式', time: '4:20 PM', active: false },
      { id: '4', title: '数据库 Schema 更新', time: '11:00 AM', active: false },
    ]
  }
];

const messages = [
  {
    id: '1',
    role: 'user',
    content: '你能帮我重构 `auth.ts` 中间件吗？我需要添加 JWT 验证。',
    timestamp: '10:30 AM'
  },
  {
    id: '2',
    role: 'assistant',
    content: "当然。这是使用 `jsonwebtoken` 添加了 JWT 验证的更新后中间件。\n\n首先，安装依赖：\n```bash\nnpm install jsonwebtoken @types/jsonwebtoken\n```\n\n然后，更新你的中间件：",
    timestamp: '10:31 AM'
  }
];

const codeSnippet = `import jwt from 'jsonwebtoken';
import { Request, Response, NextFunction } from 'express';

export const verifyToken = (req: Request, res: Response, next: NextFunction) => {
  const token = req.headers['authorization']?.split(' ')[1];

  if (!token) {
    return res.status(403).send('A token is required for authentication');
  }

  try {
    const decoded = jwt.verify(token, process.env.TOKEN_KEY!);
    req.user = decoded;
  } catch (err) {
    return res.status(401).send('Invalid Token');
  }
  return next();
};`;

// --- Components ---

interface SidebarItemProps {
  title: string;
  time: string;
  active: boolean;
}

const SidebarItem: React.FC<SidebarItemProps> = ({ title, time, active }) => (
  <div className={`group flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all ${active
    ? 'bg-blue-50 text-blue-700'
    : 'hover:bg-slate-100 text-slate-700'
    }`}>
    <MessageSquare size={16} className={active ? 'text-primary' : 'text-slate-400 group-hover:text-slate-600'} />
    <div className="flex-1 min-w-0">
      <div className={`text-sm truncate font-medium ${active ? 'text-blue-900' : 'text-slate-700'}`}>
        {title}
      </div>
      <div className="text-xs text-slate-400">{time}</div>
    </div>
    <MoreHorizontal size={14} className="text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
  </div>
);

interface ChatMessageProps {
  role: string;
  content: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ role, content }) => {
  const isUser = role === 'user';
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      <Avatar
        src={isUser ? "https://i.pravatar.cc/150?u=me" : null}
        className={isUser ? "border border-slate-200" : "bg-primary text-white"}
        icon={!isUser && <Bot size={16} />}
      />
      <div className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${isUser
        ? 'bg-primary text-white rounded-tr-none'
        : 'bg-white border border-slate-100 rounded-tl-none text-slate-800'
        }`}>
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            code({ inline, className, children, ...props }: React.ComponentPropsWithoutRef<'code'> & { inline?: boolean }) {
              const match = /language-(\w+)/.exec(className || '')
              return !inline && match ? (
                <div className="rounded-lg overflow-hidden border border-slate-200 my-4">
                  <div className="bg-slate-50 px-4 py-2 flex items-center justify-between border-b border-slate-200">
                    <span className="text-xs text-slate-500 font-mono">{match[1]}</span>
                    <Copy size={12} className="text-slate-400 cursor-pointer hover:text-slate-600" />
                  </div>
                  <SyntaxHighlighter
                    style={vscDarkPlus as unknown as Record<string, CSSProperties>}
                    language={match[1]}
                    PreTag="div"
                    customStyle={{ margin: 0, padding: '1rem', background: '#1e293b' }}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                </div>
              ) : (
                <code className={`bg-slate-100 px-1.5 py-0.5 rounded text-slate-800 font-mono text-xs border border-slate-200 ${className}`} {...props}>
                  {children}
                </code>
              )
            }
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </motion.div>
  );
};

export const AgentWorkbench: React.FC = () => {
  const [activeTab, setActiveTab] = useState('code');
  const [inputValue, setInputValue] = useState('');

  const artifactsItems = [
    {
      key: 'plan',
      label: (
        <span className="flex items-center gap-2">
          <FileText size={14} /> 计划
        </span>
      ),
      children: (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="p-4 space-y-4"
        >
          <div className="flex items-center gap-2 text-green-700 bg-green-50 p-3 rounded border border-green-200">
            <Check size={16} />
            <span className="font-mono text-sm">阶段 1: 分析完成</span>
          </div>
          <div className="prose prose-sm max-w-none text-slate-600">
            <h3 className="text-slate-900">重构计划</h3>
            <ul>
              <li>安装 <code className="text-pink-600 bg-pink-50 px-1 rounded">jsonwebtoken</code> 依赖</li>
              <li>创建中间件函数结构</li>
              <li>实现 token 提取逻辑</li>
              <li>添加缺失/无效 token 的错误处理</li>
            </ul>
          </div>
        </motion.div>
      )
    },
    {
      key: 'code',
      label: (
        <span className="flex items-center gap-2">
          <Code size={14} /> 代码
        </span>
      ),
      children: (
        <div className="relative h-full flex flex-col bg-slate-50">
          <div className="flex items-center justify-between p-2 bg-white border-b border-slate-200 text-xs text-slate-500 font-mono">
            <span>src/middleware/auth.ts</span>
            <Button type="text" size="small" icon={<Copy size={12} />} className="text-slate-400 hover:text-slate-600">复制</Button>
          </div>
          <div className="flex-1 overflow-auto p-0">
            <SyntaxHighlighter
              style={vscDarkPlus as unknown as { [key: string]: CSSProperties }}
              language="typescript"
              showLineNumbers={true}
              customStyle={{ margin: 0, padding: '1rem', background: '#1e293b', fontSize: '13px', lineHeight: '1.5', height: '100%' }}
            >
              {codeSnippet}
            </SyntaxHighlighter>
          </div>
        </div>
      )
    },
    {
      key: 'preview',
      label: (
        <span className="flex items-center gap-2">
          <Play size={14} /> 预览
        </span>
      ),
      children: (
        <div className="flex items-center justify-center h-full text-slate-400 flex-col gap-4 bg-slate-50">
          <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center border border-dashed border-slate-300">
            <Play size={24} />
          </div>
          <p className="font-mono text-xs">暂无交互式预览</p>
        </div>
      )
    }
  ];

  return (
    <div className="h-[calc(100vh-100px)] -m-6 flex bg-white overflow-hidden relative border-t border-slate-200">

      {/* Left Sidebar - History */}
      <div className="w-64 border-r border-slate-200 flex flex-col bg-white z-10">
        <div className="p-4 border-b border-slate-100">
          <Button
            type="primary"
            block
            icon={<Plus size={16} />}
            className="h-9 shadow-none"
          >
            新建会话
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-6">
          {chatHistory.map((group) => (
            <div key={group.group}>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 px-2">
                {group.group}
              </div>
              <div className="space-y-1">
                {group.items.map(item => (
                  <SidebarItem key={item.id} {...item} />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Middle - Chat Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-50 relative z-0">
        <div className="flex-1 overflow-y-auto p-6 space-y-8 pb-32">
          {messages.map(msg => (
            <ChatMessage key={msg.id} {...msg} />
          ))}
        </div>

        {/* Input Area */}
        <div className="p-6 absolute bottom-0 left-0 right-0 bg-gradient-to-t from-slate-50 via-slate-50/95 to-transparent z-20">
          <div className="relative bg-white border border-slate-200 rounded-xl focus-within:border-primary/50 focus-within:ring-2 focus-within:ring-primary/10 transition-all shadow-lg">
            <Input.TextArea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="询问关于代码的任何问题..."
              autoSize={{ minRows: 1, maxRows: 6 }}
              className="!bg-transparent !border-0 !text-slate-800 !resize-none !px-4 !py-4 focus:!shadow-none placeholder:text-slate-400"
            />
            <div className="flex items-center justify-between px-3 pb-3 pt-2 border-t border-slate-100">
              <div className="flex gap-1">
                <Tooltip title="Attach file">
                  <Button type="text" size="small" icon={<Paperclip size={16} />} className="text-slate-400 hover:text-slate-600" />
                </Tooltip>
              </div>
              <Button
                type="primary"
                size="small"
                icon={<Send size={14} />}
                className="!flex !items-center !justify-center !rounded-lg"
              />
            </div>
          </div>
          <div className="text-center mt-3 text-[10px] text-slate-400 font-mono">
            AI-AGENT v2.4.1
          </div>
        </div>
      </div>

      {/* Right - Artifacts Panel */}
      <div className="w-[500px] border-l border-slate-200 flex flex-col bg-white z-10 shadow-sm">
        <div className="flex-1 flex flex-col min-h-0">
          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={artifactsItems}
            className="flex-1 h-full"
            tabBarStyle={{
              padding: '0 16px',
              margin: 0,
              borderBottom: '1px solid #e2e8f0',
              background: '#fff'
            }}
          />
        </div>
      </div>
    </div>
  );
};
