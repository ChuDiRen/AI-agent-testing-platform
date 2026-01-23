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
  { id: '1', name: '登录模块.spec.ts', status: 'passed', duration: '12s' },
  { id: '2', name: '个人资料.spec.ts', status: 'passed', duration: '8s' },
  { id: '3', name: '支付流程.spec.ts', status: 'failed', duration: '45s' },
  { id: '4', name: '库存搜索.spec.ts', status: 'running', duration: '进行中...' },
  { id: '5', name: '购物车结算.spec.ts', status: 'pending' },
  { id: '6', name: '管理员面板.spec.ts', status: 'pending' },
];

const INITIAL_LOGS: LogEntry[] = [
  { id: '1', timestamp: new Date().toISOString(), level: 'info', message: '正在启动任务 #1024...' },
  { id: '2', timestamp: new Date().toISOString(), level: 'info', message: '当前环境: 测试环境 (Staging v2.4.0)' },
  { id: '3', timestamp: new Date().toISOString(), level: 'debug', message: '正在从 /etc/config/test-runner.json 加载配置' },
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
        '正在等待元素选择器 ".submit-btn" 可见...',
        'GET /api/v1/users/me 200 OK (45ms)',
        '正在点击元素 "提交订单"',
        '正在验证页面标题是否等于 "订单确认"',
        '正在模拟支付网关响应...',
        '截图已保存至 /artifacts/screenshots/failure_1.png'
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
      case 'running': return <PauseCircle className="animate-pulse text-blue-500" size={16} />;
      case 'passed': return <CheckCircle className="text-emerald-500" size={16} />;
      case 'failed': return <XCircle className="text-red-500" size={16} />;
      case 'pending': return <Clock className="text-slate-400" size={16} />;
    }
  };

  const getLogColor = (level: LogEntry['level']) => {
    switch (level) {
      case 'info': return 'text-slate-300';
      case 'warn': return 'text-amber-400';
      case 'error': return 'text-red-400';
      case 'success': return 'text-emerald-400';
      case 'debug': return 'text-blue-400';
      default: return 'text-slate-300';
    }
  };

  return (
    <div className="h-[calc(100vh-140px)] flex flex-col gap-4 animate-fade-in p-6 pt-0">
      {/* Header Stats */}
      <div className="flex justify-between items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Terminal className="text-blue-600" />
            <Title level={4} className="!text-slate-800 !m-0">实时运行控制台</Title>
          </div>
          <div className="h-6 w-px bg-slate-200 mx-2" />
          <div className="flex gap-4 text-sm">
            <span className="flex items-center gap-2 text-slate-600">
              <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-sm"></span>
              已通过: <span className="font-mono font-bold text-emerald-600">{stats.passed}</span>
            </span>
            <span className="flex items-center gap-2 text-slate-600">
              <span className="w-2 h-2 rounded-full bg-red-500 shadow-sm"></span>
              已失败: <span className="font-mono font-bold text-red-600">{stats.failed}</span>
            </span>
            <span className="flex items-center gap-2 text-slate-600">
              <span className="w-2 h-2 rounded-full bg-blue-500 shadow-sm"></span>
              运行中: <span className="font-mono font-bold text-blue-600">{stats.running}</span>
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Text className="text-slate-500 text-sm">自动滚动</Text>
            <Switch
              checked={autoScroll}
              onChange={setAutoScroll}
              size="small"
            />
          </div>
          <Button type="text" icon={<Download size={16} />} title="下载日志" className="text-slate-400 hover:text-slate-700" />
          <Button type="text" icon={<Trash2 size={16} />} title="清空日志" className="text-slate-400 hover:text-red-500" onClick={() => setLogs([])} />
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex gap-4 min-h-0">
        {/* Terminal Window */}
        <div className="flex-1 bg-[#1e293b] rounded-xl border border-slate-700 overflow-hidden flex flex-col shadow-lg">
          <div className="bg-[#0f172a] p-2 border-b border-slate-700 flex justify-between items-center px-4">
            <div className="flex gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
              <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
            </div>
            <Text className="text-xs text-slate-400 font-mono">runner-process-1024</Text>
          </div>

          <div className="flex-1 overflow-y-auto p-4 font-mono text-sm space-y-1 custom-scrollbar">
            {logs.map((log) => (
              <div key={log.id} className="flex gap-3 hover:bg-white/5 px-2 py-0.5 rounded transition-colors">
                <span className="text-slate-500 shrink-0 select-none">
                  {dayjs(log.timestamp).format('HH:mm:ss.SSS')}
                </span>
                <span className={`shrink-0 w-16 font-bold uppercase text-[10px] pt-0.5 ${log.level === 'error' ? 'text-red-400' :
                  log.level === 'warn' ? 'text-amber-400' :
                    log.level === 'success' ? 'text-emerald-400' :
                      log.level === 'debug' ? 'text-blue-400' : 'text-slate-400'
                  }`}>
                  {log.level === 'error' ? '错误' :
                    log.level === 'warn' ? '警告' :
                      log.level === 'success' ? '通过' :
                        log.level === 'debug' ? '调试' : '日志'}
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
        <div className="w-80 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col">
          <div className="p-4 border-b border-slate-100">
            <Text className="text-slate-700 font-medium flex items-center gap-2">
              <FileCode size={16} className="text-blue-600" />
              测试文件列表
            </Text>
          </div>
          <div className="flex-1 overflow-y-auto p-2">
            <List
              dataSource={testFiles}
              renderItem={(item) => (
                <List.Item className="!border-b-0 !p-2">
                  <div className={`w-full p-3 rounded-lg border flex items-center justify-between group transition-all ${item.status === 'running'
                    ? 'bg-blue-50 border-blue-200 shadow-sm'
                    : 'bg-white border-slate-100 hover:bg-slate-50 hover:border-slate-200'
                    }`}>
                    <div className="flex items-center gap-3 overflow-hidden">
                      {getStatusIcon(item.status)}
                      <div className="flex flex-col min-w-0">
                        <Text className={`text-sm font-medium truncate ${item.status === 'running' ? 'text-blue-700' : 'text-slate-700'}`}>
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
