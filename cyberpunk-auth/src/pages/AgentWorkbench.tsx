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
  Check
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import '../components/Tabs.css';

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
      { id: '3', title: '新功能：深色模式', time: '4:20 PM', active: false },
      { id: '4', title: '数据库架构更新', time: '11:00 AM', active: false },
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
    content: "当然，我可以帮你。这是包含 JWT 验证的中间件更新版本，使用 `jsonwebtoken` 库。\n\n首先，确保安装包：\n```bash\nnpm install jsonwebtoken @types/jsonwebtoken\n```\n\n然后，更新你的中间件：",
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
  <div className={`group flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all ${
    active ? 'bg-indigo-500/10 border border-indigo-500/20' : 'hover:bg-slate-800 border border-transparent'
  }`}>
    <MessageSquare size={16} className={active ? 'text-indigo-400' : 'text-slate-500'} />
    <div className="flex-1 min-w-0">
      <div className={`text-sm truncate ${active ? 'text-indigo-100 font-medium' : 'text-slate-300'}`}>
        {title}
      </div>
      <div className="text-xs text-slate-500">{time}</div>
    </div>
    <MoreHorizontal size={14} className="text-slate-500 opacity-0 group-hover:opacity-100" />
  </div>
);

interface ChatMessageProps {
  role: string;
  content: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ role, content }) => {
  const isUser = role === 'user';
  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
      <Avatar 
        src={isUser ? "https://i.pravatar.cc/150?u=me" : null}
        className={isUser ? "border border-slate-600" : "bg-indigo-600"}
        icon={!isUser && <Code size={16} />}
      />
      <div className={`max-w-[80%] rounded-2xl p-4 ${
        isUser 
          ? 'bg-indigo-600 text-white rounded-tr-none' 
          : 'bg-slate-800 border border-slate-700 rounded-tl-none'
      }`}>
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            code({inline, className, children, ...props}: React.ComponentPropsWithoutRef<'code'> & { inline?: boolean }) {
              const match = /language-(\w+)/.exec(className || '')
              return !inline && match ? (
                <SyntaxHighlighter
                  style={vscDarkPlus as unknown as Record<string, CSSProperties>}
                  language={match[1]}
                  PreTag="div"
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              )
            }
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
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
          <FileText size={14} /> Plan
        </span>
      ),
      children: (
        <div className="p-4 space-y-4">
          <div className="flex items-center gap-2 text-sm text-green-400 bg-green-900/20 p-3 rounded border border-green-900/50">
             <Check size={16} />
             <span>Phase 1: Analysis Completed</span>
          </div>
          <div className="prose prose-invert prose-sm">
            <h3>Refactoring Plan</h3>
            <ul>
               <li>Install <code>jsonwebtoken</code> dependency</li>
               <li>Create middleware function structure</li>
               <li>Implement token extraction logic</li>
               <li>Add error handling for missing/invalid tokens</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      key: 'code',
      label: (
        <span className="flex items-center gap-2">
          <Code size={14} /> Code
        </span>
      ),
      children: (
        <div className="relative h-full flex flex-col">
           <div className="flex items-center justify-between p-2 bg-slate-900 border-b border-slate-800 text-xs text-slate-400">
             <span>src/middleware/auth.ts</span>
             <Button type="text" size="small" icon={<Copy size={12} />} className="!text-slate-400 hover:!text-white">Copy</Button>
           </div>
           <div className="flex-1 overflow-auto bg-[#1e1e1e] p-0">
             <SyntaxHighlighter
                style={vscDarkPlus as unknown as { [key: string]: CSSProperties }}
                language="typescript"
                showLineNumbers={true}
                customStyle={{ margin: 0, padding: '1rem', background: 'transparent' }}
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
          <Play size={14} /> Preview
        </span>
      ),
      children: (
        <div className="flex items-center justify-center h-full text-slate-500 flex-col gap-4">
           <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center border border-dashed border-slate-600">
             <Play size={24} />
           </div>
           <p>No interactive preview available for middleware</p>
        </div>
      )
    }
  ];

  return (
    <div className="h-[calc(100vh-64px)] -m-6 flex bg-slate-950">
      
      {/* Left Sidebar - History */}
      <div className="w-64 border-r border-slate-800 flex flex-col bg-slate-900/50">
        <div className="p-4 border-b border-slate-800">
          <Button 
            type="primary" 
            block 
            icon={<Plus size={16} />}
            className="!bg-indigo-600 hover:!bg-indigo-500 !border-0 !h-9"
          >
            New Chat
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-6">
          {chatHistory.map((group) => (
            <div key={group.group}>
              <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-2">
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
      <div className="flex-1 flex flex-col min-w-0 bg-slate-950">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map(msg => (
            <ChatMessage key={msg.id} {...msg} />
          ))}
        </div>
        
        {/* Input Area */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/80 backdrop-blur-sm">
          <div className="relative bg-slate-900 border border-slate-700 rounded-xl focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/50 transition-all">
             <Input.TextArea 
               value={inputValue}
               onChange={(e) => setInputValue(e.target.value)}
               placeholder="Ask anything about your code..."
               autoSize={{ minRows: 1, maxRows: 6 }}
               className="!bg-transparent !border-0 !text-slate-200 !resize-none !px-4 !py-3 focus:!shadow-none"
             />
             <div className="flex items-center justify-between px-3 pb-3">
               <div className="flex gap-1">
                 <Tooltip title="Attach file">
                   <Button type="text" size="small" icon={<Paperclip size={16} />} className="!text-slate-400 hover:!text-white" />
                 </Tooltip>
               </div>
               <Button 
                 type="primary" 
                 size="small" 
                 icon={<Send size={14} />} 
                 className="!bg-indigo-600 hover:!bg-indigo-500 !border-0"
               />
             </div>
          </div>
          <div className="text-center mt-2 text-xs text-slate-500">
             AI can make mistakes. Please review generated code.
          </div>
        </div>
      </div>

      {/* Right - Artifacts Panel */}
      <div className="w-[450px] border-l border-slate-800 flex flex-col bg-slate-900">
        <div className="flex-1 flex flex-col min-h-0">
          <Tabs 
            activeKey={activeTab} 
            onChange={setActiveTab}
            items={artifactsItems} 
            className="flex-1 custom-tabs h-full"
            tabBarStyle={{ 
              padding: '0 16px', 
              margin: 0, 
              borderBottom: '1px solid #1e293b',
              background: '#0f172a'
            }}
          />
        </div>
      </div>
    </div>
  );
};
