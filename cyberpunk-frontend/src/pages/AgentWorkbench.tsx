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
  Sparkles
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { motion } from 'framer-motion';
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
    active 
      ? 'bg-neon-cyan/10 border border-neon-cyan/30 shadow-[0_0_10px_rgba(0,243,255,0.1)]' 
      : 'hover:bg-slate-800/50 border border-transparent hover:border-slate-700'
  }`}>
    <MessageSquare size={16} className={active ? 'text-neon-cyan' : 'text-slate-500 group-hover:text-neon-cyan/70 transition-colors'} />
    <div className="flex-1 min-w-0">
      <div className={`text-sm truncate transition-colors ${active ? 'text-white font-medium' : 'text-slate-300 group-hover:text-white'}`}>
        {title}
      </div>
      <div className="text-xs text-slate-500">{time}</div>
    </div>
    <MoreHorizontal size={14} className="text-slate-500 opacity-0 group-hover:opacity-100 transition-opacity" />
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
        className={isUser ? "border-2 border-slate-700 ring-2 ring-transparent" : "bg-neon-cyan text-black border-2 border-neon-cyan shadow-[0_0_10px_rgba(0,243,255,0.3)]"}
        icon={!isUser && <Sparkles size={16} />}
      />
      <div className={`max-w-[80%] rounded-2xl p-5 shadow-lg ${
        isUser 
          ? 'bg-gradient-to-br from-neon-cyan/80 to-blue-600/80 text-white rounded-tr-none backdrop-blur-md border border-white/10' 
          : 'bg-slate-800/80 border border-slate-700/50 rounded-tl-none backdrop-blur-md'
      }`}>
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={{
            code({inline, className, children, ...props}: React.ComponentPropsWithoutRef<'code'> & { inline?: boolean }) {
              const match = /language-(\w+)/.exec(className || '')
              return !inline && match ? (
                <div className="rounded-lg overflow-hidden border border-slate-700 my-4 shadow-xl">
                    <div className="bg-slate-900/80 px-4 py-2 flex items-center justify-between border-b border-slate-700">
                        <span className="text-xs text-slate-400 font-mono">{match[1]}</span>
                        <Copy size={12} className="text-slate-500 cursor-pointer hover:text-white" />
                    </div>
                    <SyntaxHighlighter
                      style={vscDarkPlus as unknown as Record<string, CSSProperties>}
                      language={match[1]}
                      PreTag="div"
                      customStyle={{ margin: 0, padding: '1rem', background: '#0a0a0a' }}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                </div>
              ) : (
                <code className={`bg-slate-900/50 px-1.5 py-0.5 rounded text-neon-cyan font-mono text-xs border border-slate-700/50 ${className}`} {...props}>
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
          <FileText size={14} /> Plan
        </span>
      ),
      children: (
        <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="p-4 space-y-4"
        >
          <div className="flex items-center gap-2 text-neon-green bg-neon-green/10 p-3 rounded border border-neon-green/20 shadow-[0_0_10px_rgba(10,255,10,0.1)]">
             <Check size={16} />
             <span className="font-mono text-sm">Phase 1: Analysis Completed</span>
          </div>
          <div className="prose prose-invert prose-sm max-w-none">
            <h3 className="text-white font-display">Refactoring Plan</h3>
            <ul className="text-slate-300">
               <li>Install <code className="text-neon-cyan">jsonwebtoken</code> dependency</li>
               <li>Create middleware function structure</li>
               <li>Implement token extraction logic</li>
               <li>Add error handling for missing/invalid tokens</li>
            </ul>
          </div>
        </motion.div>
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
        <div className="relative h-full flex flex-col bg-[#050505]">
           <div className="flex items-center justify-between p-2 bg-slate-900/50 border-b border-slate-800 text-xs text-slate-400 font-mono">
             <span>src/middleware/auth.ts</span>
             <Button type="text" size="small" icon={<Copy size={12} />} className="!text-slate-400 hover:!text-white">Copy</Button>
           </div>
           <div className="flex-1 overflow-auto p-0 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent">
             <SyntaxHighlighter
                style={vscDarkPlus as unknown as { [key: string]: CSSProperties }}
                language="typescript"
                showLineNumbers={true}
                customStyle={{ margin: 0, padding: '1rem', background: 'transparent', fontSize: '13px', lineHeight: '1.5' }}
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
           <div className="w-16 h-16 rounded-full bg-slate-800/50 flex items-center justify-center border border-dashed border-slate-600 animate-pulse">
             <Play size={24} />
           </div>
           <p className="font-mono text-xs">No interactive preview available</p>
        </div>
      )
    }
  ];

  return (
    <div className="h-[calc(100vh-100px)] -m-6 flex bg-cyber-black overflow-hidden relative">
      {/* Background Grid */}
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-5 pointer-events-none" />
      
      {/* Left Sidebar - History */}
      <motion.div 
        initial={{ x: -20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="w-72 border-r border-slate-800/50 flex flex-col bg-slate-900/40 backdrop-blur-xl z-10"
      >
        <div className="p-4 border-b border-slate-800/50">
          <Button 
            type="primary" 
            block 
            icon={<Plus size={16} />}
            className="cyber-button !h-10 !border-none shadow-[0_0_15px_rgba(0,243,255,0.2)]"
          >
            New Chat
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto p-3 space-y-6 custom-scrollbar">
          {chatHistory.map((group) => (
            <div key={group.group}>
              <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3 px-2 font-display">
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
      </motion.div>

      {/* Middle - Chat Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-transparent relative z-0">
        <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar pb-32">
          {messages.map(msg => (
            <ChatMessage key={msg.id} {...msg} />
          ))}
        </div>
        
        {/* Input Area */}
        <div className="p-6 absolute bottom-0 left-0 right-0 bg-gradient-to-t from-cyber-black via-cyber-black/95 to-transparent z-20">
          <div className="relative bg-slate-900/80 border border-slate-700/50 rounded-xl focus-within:border-neon-cyan/50 focus-within:ring-1 focus-within:ring-neon-cyan/20 transition-all shadow-2xl backdrop-blur-md">
             <Input.TextArea 
               value={inputValue}
               onChange={(e) => setInputValue(e.target.value)}
               placeholder="Ask anything about your code..."
               autoSize={{ minRows: 1, maxRows: 6 }}
               className="!bg-transparent !border-0 !text-slate-200 !resize-none !px-4 !py-4 focus:!shadow-none placeholder:text-slate-600"
             />
             <div className="flex items-center justify-between px-3 pb-3 pt-2 border-t border-slate-800/50">
               <div className="flex gap-1">
                 <Tooltip title="Attach file">
                   <Button type="text" size="small" icon={<Paperclip size={16} />} className="!text-slate-400 hover:!text-neon-cyan transition-colors" />
                 </Tooltip>
               </div>
               <Button 
                 type="primary" 
                 size="small" 
                 icon={<Send size={14} />} 
                 className="!bg-neon-cyan hover:!bg-neon-cyan/90 !text-black !border-0 !h-8 !w-8 !flex !items-center !justify-center !rounded-lg"
               />
             </div>
          </div>
          <div className="text-center mt-3 text-[10px] text-slate-600 font-mono">
             AI-AGENT v2.4.1 // SYSTEM ONLINE
          </div>
        </div>
      </div>

      {/* Right - Artifacts Panel */}
      <motion.div 
        initial={{ x: 20, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        className="w-[500px] border-l border-slate-800/50 flex flex-col bg-slate-950/80 backdrop-blur-md z-10 shadow-[-10px_0_30px_rgba(0,0,0,0.5)]"
      >
        <div className="flex-1 flex flex-col min-h-0">
          <Tabs 
            activeKey={activeTab} 
            onChange={setActiveTab}
            items={artifactsItems} 
            className="flex-1 custom-tabs h-full"
            tabBarStyle={{ 
              padding: '0 16px', 
              margin: 0, 
              borderBottom: '1px solid rgba(30, 41, 59, 0.5)',
              background: 'rgba(15, 23, 42, 0.8)'
            }}
          />
        </div>
      </motion.div>
    </div>
  );
};

