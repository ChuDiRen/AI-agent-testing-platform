import React, { useState, useEffect, useRef } from 'react';
import { Switch, Typography, List, Button } from 'antd';
import { 
  Terminal, 
  CheckCircle, 
  XCircle, 
  Clock, 
  PauseCircle, 
  Download,
  Trash2,
  FileCode
} from 'lucide-react';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

// --- Types ---
interface LogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'warn' | 'error' | 'debug' | 'success';
  message: string;
}

interface TestFile {
  id: string;
  name: string;
  status: 'running' | 'passed' | 'failed' | 'pending';
  duration?: string;
}

// --- Mock Data ---
const MOCK_TEST_FILES: TestFile[] = [
  { id: '1', name: 'auth.spec.ts', status: 'passed', duration: '12s' },
  { id: '2', name: 'user_profile.spec.ts', status: 'passed', duration: '8s' },
  { id: '3', name: 'payment_flow.spec.ts', status: 'failed', duration: '45s' },
  { id: '4', name: 'inventory_search.spec.ts', status: 'running', duration: '运行中...' },
  { id: '5', name: 'cart_checkout.spec.ts', status: 'pending' },
  { id: '6', name: 'admin_dashboard.spec.ts', status: 'pending' },
];

const INITIAL_LOGS: LogEntry[] = [
  { id: '1', timestamp: new Date().toISOString(), level: 'info', message: '开始执行任务 #1024...' },
  { id: '2', timestamp: new Date().toISOString(), level: 'info', message: '环境：Staging (v2.4.0)' },
  { id: '3', timestamp: new Date().toISOString(), level: 'debug', message: '从 /etc/config/test-runner.json 加载配置' },
  { id: '4', timestamp: new Date().toISOString(), level: 'success', message: '配置加载成功。' },
];

const LiveExecutionConsole: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>(INITIAL_LOGS);
  const [autoScroll, setAutoScroll] = useState(true);
  const [testFiles] = useState<TestFile[]>(MOCK_TEST_FILES);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // --- Stats Calculation ---
  const stats = {
    passed: testFiles.filter(f => f.status === 'passed').length,
    failed: testFiles.filter(f => f.status === 'failed').length,
    pending: testFiles.filter(f => f.status === 'pending').length,
    running: testFiles.filter(f => f.status === 'running').length,
    total: testFiles.length
  };

  // --- Auto-scroll Effect ---
  useEffect(() => {
    if (autoScroll) {
      logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  // --- Log Simulation Effect ---
  useEffect(() => {
    const interval = setInterval(() => {
      const levels: LogEntry['level'][] = ['info', 'debug', 'success', 'warn'];
      const messages = [
        'Waiting for element selector ".submit-btn" to be visible...',
        'GET /api/v1/users/me 200 OK (45ms)',
        'Clicking element "Submit Order"',
        'Verifying page title equals "Order Confirmation"',
        'Mocking payment gateway response...',
        'Screenshot saved to /artifacts/screenshots/failure_1.png'
      ];
      
      const randomLevel = levels[Math.floor(Math.random() * levels.length)];
      const randomMessage = messages[Math.floor(Math.random() * messages.length)];

      const newLog: LogEntry = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        level: randomLevel,
        message: randomMessage
      };

      setLogs(prev => [...prev, newLog]);
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: TestFile['status']) => {
    switch (status) {
      case 'running': return <PauseCircle className="animate-pulse text-blue-400" size={16} />;
      case 'passed': return <CheckCircle className="text-green-400" size={16} />;
      case 'failed': return <XCircle className="text-red-400" size={16} />;
      case 'pending': return <Clock className="text-slate-500" size={16} />;
    }
  };

  const getLogColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'info': return 'text-slate-300';
      case 'warn': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      case 'success': return 'text-green-400';
      case 'debug': return 'text-neon-purple';
      default: return 'text-slate-300';
    }
  };

  return (
    <div className="h-[calc(100vh-140px)] flex flex-col gap-4 animate-fade-in">
      {/* Header Stats */}
      <div className="flex justify-between items-center bg-slate-900/50 p-4 rounded-xl border border-slate-800 backdrop-blur-sm">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
             <Terminal className="text-neon-cyan" />
             <Title level={4} className="!text-slate-100 !m-0">Live Execution Console</Title>
          </div>
          <div className="h-6 w-px bg-slate-700 mx-2" />
          <div className="flex gap-4 text-sm">
            <span className="flex items-center gap-2 text-slate-300">
               <span className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]"></span>
               Passed: <span className="font-mono font-bold text-green-400">{stats.passed}</span>
            </span>
            <span className="flex items-center gap-2 text-slate-300">
               <span className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]"></span>
               Failed: <span className="font-mono font-bold text-red-400">{stats.failed}</span>
            </span>
             <span className="flex items-center gap-2 text-slate-300">
               <span className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></span>
               Running: <span className="font-mono font-bold text-blue-400">{stats.running}</span>
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
           <div className="flex items-center gap-2">
             <Text className="text-slate-400 text-sm">Auto-scroll</Text>
             <Switch 
               checked={autoScroll} 
               onChange={setAutoScroll} 
               size="small" 
               className="bg-slate-700"
             />
           </div>
           <Button type="text" icon={<Download size={16} />} className="text-slate-400 hover:text-white" />
           <Button type="text" icon={<Trash2 size={16} />} className="text-slate-400 hover:text-red-400" onClick={() => setLogs([])} />
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex gap-4 min-h-0">
        {/* Terminal Window */}
        <div className="flex-1 bg-black/80 rounded-xl border border-slate-800 overflow-hidden flex flex-col shadow-2xl">
          <div className="bg-slate-900/80 p-2 border-b border-slate-800 flex justify-between items-center px-4">
             <div className="flex gap-2">
               <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50"></div>
               <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50"></div>
               <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50"></div>
             </div>
             <Text className="text-xs text-slate-500 font-mono">runner-process-1024</Text>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 font-mono text-sm space-y-1 custom-scrollbar">
             {logs.map((log) => (
               <div key={log.id} className="flex gap-3 hover:bg-white/5 px-2 py-0.5 rounded transition-colors">
                  <span className="text-slate-600 shrink-0 select-none">
                    {dayjs(log.timestamp).format('HH:mm:ss.SSS')}
                  </span>
                  <span className={`shrink-0 w-16 font-bold uppercase text-[10px] pt-0.5 ${
                    log.level === 'error' ? 'text-red-500' : 
                    log.level === 'warn' ? 'text-yellow-500' :
                    log.level === 'success' ? 'text-green-500' : 
                    log.level === 'debug' ? 'text-cyan-500' : 'text-blue-500'
                  }`}>
                    {log.level}
                  </span>
                  <span className={`${getLogColor(log.level)} break-all`}>
                    {log.message}
                  </span>
               </div>
             ))}
             <div ref={logsEndRef} />
          </div>
        </div>

        {/* Sidebar: Test Files */}
        <div className="w-80 bg-slate-900/50 rounded-xl border border-slate-800 backdrop-blur-sm flex flex-col">
           <div className="p-4 border-b border-slate-800">
             <Text className="text-slate-300 font-medium flex items-center gap-2">
               <FileCode size={16} className="text-neon-cyan" />
               Test Files
             </Text>
           </div>
           <div className="flex-1 overflow-y-auto p-2">
              <List
                dataSource={testFiles}
                renderItem={(item) => (
                  <List.Item className="!border-b-0 !p-2">
                    <div className={`w-full p-3 rounded-lg border flex items-center justify-between group transition-all ${
                      item.status === 'running' 
                        ? 'bg-neon-cyan/10 border-neon-cyan/30 shadow-[0_0_10px_rgba(99,102,241,0.1)]' 
                        : 'bg-slate-800/30 border-slate-700/30 hover:bg-slate-800/60'
                    }`}>
                       <div className="flex items-center gap-3 overflow-hidden">
                          {getStatusIcon(item.status)}
                          <div className="flex flex-col min-w-0">
                             <Text className={`text-sm font-medium truncate ${item.status === 'running' ? 'text-indigo-300' : 'text-slate-300'}`}>
                               {item.name}
                             </Text>
                             <Text className="text-xs text-slate-500">
                               {item.duration || '--'}
                             </Text>
                          </div>
                       </div>
                    </div>
                  </List.Item>
                )}
              />
           </div>
        </div>
      </div>
    </div>
  );
};

export default LiveExecutionConsole;

