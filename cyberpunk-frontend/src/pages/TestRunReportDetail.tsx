import React, { useState } from 'react';
import { Card, Tabs, Collapse, Tag, Typography, Button, Alert, Image, Progress, Statistic } from 'antd';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Calendar, 
  Bot, 
  FileText, 
  Download, 
  ChevronRight, 
  Terminal,
  ImageIcon
} from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const { Title, Text } = Typography;

// --- Types ---
interface TestCase {
  id: string;
  name: string;
  suite: string;
  status: 'passed' | 'failed' | 'skipped';
  duration: string;
  error?: {
    message: string;
    stackTrace: string;
  };
  screenshotUrl?: string;
  aiAnalysis?: string;
}

interface TestRunSummary {
  id: string;
  name: string;
  startTime: string;
  duration: string;
  total: number;
  passed: number;
  failed: number;
  skipped: number;
  environment: string;
}

// --- Mock Data ---
const MOCK_SUMMARY: TestRunSummary = {
  id: 'run-2048',
  name: '端到端支付网关验证',
  startTime: '2025-05-14 10:30:00',
  duration: '4m 12s',
  total: 45,
  passed: 42,
  failed: 2,
  skipped: 1,
  environment: 'Staging'
};

const MOCK_FAILED_CASES: TestCase[] = [
  {
    id: 'tc-101',
    name: '验证信用卡支付流程',
    suite: '结账模块',
    status: 'failed',
    duration: '12s',
    error: {
      message: '断言错误：期望支付状态为"已完成"但得到"失败"',
      stackTrace: `错误：期望支付状态为"已完成"但得到"失败"
    at PaymentPage.verifyStatus (src/pages/payment.page.ts:45:12)
    at async TestRunner.execute (src/runner/core.ts:120:5)
    at async Suite.run (src/runner/suite.ts:34:9)`
    },
    screenshotUrl: 'https://placehold.co/600x400/1e293b/ef4444?text=Payment+Failure+Screenshot',
    aiAnalysis: '支付网关返回了"失败"状态。基于日志，模拟服务器响应了 402 Payment Required 错误，暗示使用的测试信用卡号（以 4242 结尾）可能在 Staging 环境中配置为触发拒绝。建议：验证"Staging"环境的测试数据配置。'
  },
  {
    id: 'tc-102',
    name: '检查库存预留',
    suite: '库存模块',
    status: 'failed',
    duration: '5s',
    error: {
      message: '超时错误：5000ms 后未找到元素".stock-badge"',
      stackTrace: `超时错误：5000ms 后未找到元素".stock-badge"
    at InventoryPage.checkBadge (src/pages/inventory.page.ts:22:8)
    at async Context.<anonymous> (src/tests/inventory.spec.ts:15:3)`
    },
    aiAnalysis: '元素".stock-badge"未能出现。这通常发生在页面加载比预期慢或产品实际缺货的情况下。网络日志显示库存 API 返回 200 OK，但响应体有"quantity: 0"。测试期望"quantity > 0"。'
  }
];

const MOCK_PASSED_CASES: TestCase[] = Array(10).fill(null).map((_, i) => ({
  id: `tc-20${i}`,
  name: `成功的测试用例 #${i + 1}`,
  suite: '通用模块',
  status: 'passed',
  duration: `${Math.floor(Math.random() * 500) + 100}ms`
}));

const TestRunReportDetail: React.FC = () => {
  const [activeTab, setActiveTab] = useState('failed');

  const renderScorecard = () => (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
        <Statistic 
          title={<span className="text-slate-400 text-xs uppercase tracking-wider">Pass Rate</span>}
          value={((MOCK_SUMMARY.passed / MOCK_SUMMARY.total) * 100).toFixed(1)}
          suffix="%"
          styles={{ content: { color: '#4ade80', fontWeight: 'bold' } }}
          prefix={<CheckCircle size={20} />}
        />
        <Progress percent={Math.round((MOCK_SUMMARY.passed / MOCK_SUMMARY.total) * 100)} showInfo={false} strokeColor="#4ade80" railColor="rgba(255,255,255,0.1)" size="small" className="mt-2" />
      </Card>
      
      <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
        <Statistic 
          title={<span className="text-slate-400 text-xs uppercase tracking-wider">Total Duration</span>}
          value={MOCK_SUMMARY.duration}
          styles={{ content: { color: '#cbd5e1' } }}
          prefix={<Clock size={20} className="text-blue-400" />}
        />
        <div className="text-xs text-slate-500 mt-2">Avg. 120ms per test</div>
      </Card>

      <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
        <Statistic 
          title={<span className="text-slate-400 text-xs uppercase tracking-wider">Start Time</span>}
          value={MOCK_SUMMARY.startTime}
          styles={{ content: { color: '#cbd5e1', fontSize: '1.25rem' } }}
          prefix={<Calendar size={20} className="text-purple-400" />}
        />
        <div className="text-xs text-slate-500 mt-2">{MOCK_SUMMARY.environment} Env</div>
      </Card>

      <Card className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm">
         <div className="flex flex-col h-full justify-between">
            <span className="text-slate-400 text-xs uppercase tracking-wider">Results Summary</span>
            <div className="flex gap-2 mt-2">
               <div className="flex-1 bg-green-500/10 border border-green-500/20 rounded p-2 text-center">
                  <div className="text-green-400 font-bold text-lg">{MOCK_SUMMARY.passed}</div>
                  <div className="text-[10px] text-green-500/70 uppercase">Passed</div>
               </div>
               <div className="flex-1 bg-red-500/10 border border-red-500/20 rounded p-2 text-center">
                  <div className="text-red-400 font-bold text-lg">{MOCK_SUMMARY.failed}</div>
                  <div className="text-[10px] text-red-500/70 uppercase">Failed</div>
               </div>
               <div className="flex-1 bg-slate-700/30 border border-slate-600/30 rounded p-2 text-center">
                  <div className="text-slate-300 font-bold text-lg">{MOCK_SUMMARY.skipped}</div>
                  <div className="text-[10px] text-slate-400/70 uppercase">Skip</div>
               </div>
            </div>
         </div>
      </Card>
    </div>
  );

  const renderFailedCases = () => (
    <Collapse 
      defaultActiveKey={MOCK_FAILED_CASES.map(c => c.id)} 
      className="bg-transparent border-none"
      expandIcon={({ isActive }) => <ChevronRight size={16} className={`text-slate-500 transition-transform ${isActive ? 'rotate-90' : ''}`} />}
      items={MOCK_FAILED_CASES.map(testCase => ({
        key: testCase.id,
        label: (
          <div className="flex items-center gap-3 py-1">
             <XCircle className="text-red-500" size={18} />
             <span className="text-slate-200 font-medium text-base">{testCase.name}</span>
             <Tag className="bg-slate-800 border-slate-700 text-slate-400 ml-auto">{testCase.suite}</Tag>
             <span className="text-slate-500 text-xs font-mono">{testCase.duration}</span>
          </div>
        ),
        className: "bg-slate-900/40 border border-red-900/30 rounded-lg mb-4 !overflow-hidden backdrop-blur-sm",
        style: { borderBottom: '1px solid rgba(127, 29, 29, 0.3)' },
        children: (
          <div className="flex flex-col gap-4 p-2">
            {/* Error Message */}
            <Alert
              title={<span className="font-mono font-bold text-red-400">Error</span>}
              description={<span className="font-mono text-red-300">{testCase.error?.message}</span>}
              type="error"
              showIcon
              className="bg-red-950/30 border-red-900/50"
            />

            {/* AI Analysis */}
            {testCase.aiAnalysis && (
              <div className="bg-indigo-950/30 border border-neon-cyan/30 rounded-lg p-4 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-neon-cyan"></div>
                <div className="flex gap-3">
                  <Bot className="text-neon-cyan shrink-0 mt-1" size={20} />
                  <div>
                    <h4 className="text-indigo-300 font-medium mb-1">AI Root Cause Analysis</h4>
                    <p className="text-slate-300 text-sm leading-relaxed">
                      {testCase.aiAnalysis}
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="flex gap-6 mt-2">
               {/* Stack Trace */}
               <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2 text-slate-400 text-sm">
                    <Terminal size={14} /> Stack Trace
                  </div>
                  <div className="rounded-lg overflow-hidden border border-slate-700/50">
                    <SyntaxHighlighter 
                      language="typescript" 
                      style={vscDarkPlus}
                      customStyle={{ margin: 0, padding: '1rem', fontSize: '12px', background: '#0f172a' }}
                    >
                      {testCase.error?.stackTrace || ''}
                    </SyntaxHighlighter>
                  </div>
               </div>

               {/* Screenshot */}
               {testCase.screenshotUrl && (
                 <div className="w-80 shrink-0">
                    <div className="flex items-center gap-2 mb-2 text-slate-400 text-sm">
                      <ImageIcon size={14} /> Failure Screenshot
                    </div>
                    <Image 
                      src={testCase.screenshotUrl} 
                      className="rounded-lg border border-slate-700/50"
                      alt="Failure Screenshot"
                    />
                 </div>
               )}
            </div>
          </div>
        )
      }))}
    />
  );

  const renderAllResults = () => (
    <div className="bg-slate-900/40 rounded-lg border border-slate-800 overflow-hidden">
       {MOCK_PASSED_CASES.map((tc, idx) => (
         <div key={tc.id} className={`flex items-center justify-between p-4 ${idx !== MOCK_PASSED_CASES.length - 1 ? 'border-b border-slate-800' : ''} hover:bg-slate-800/30 transition-colors`}>
            <div className="flex items-center gap-3">
              <CheckCircle className="text-green-500" size={16} />
              <span className="text-slate-300">{tc.name}</span>
            </div>
            <div className="flex items-center gap-4">
              <Tag className="bg-slate-800 border-slate-700 text-slate-500 m-0">{tc.suite}</Tag>
              <span className="text-slate-500 font-mono text-xs w-12 text-right">{tc.duration}</span>
            </div>
         </div>
       ))}
    </div>
  );

  return (
    <div className="animate-fade-in space-y-6">
      <div className="flex justify-between items-start">
        <div>
           <Title level={2} className="!text-slate-100 !mb-1">{MOCK_SUMMARY.name}</Title>
           <Text className="text-slate-400">Run ID: #{MOCK_SUMMARY.id} • {MOCK_SUMMARY.startTime}</Text>
        </div>
        <div className="flex gap-2">
           <Button icon={<Download size={16} />} className="text-slate-300 border-slate-700 bg-slate-800 hover:text-white hover:border-slate-600">Export Report</Button>
           <Button type="primary" className="bg-neon-cyan hover:bg-neon-cyan">Rerun Failed</Button>
        </div>
      </div>

      {renderScorecard()}

      <Tabs 
        activeKey={activeTab} 
        onChange={setActiveTab}
        type="card"
        className="cyberpunk-tabs"
        items={[
          {
            key: 'overview',
            label: 'Overview',
            children: <div className="text-slate-400 p-4">Overview charts and trends would go here...</div>
          },
          {
            key: 'failed',
            label: (
              <span className="flex items-center gap-2">
                Failed Cases 
                <Tag color="#ef4444" className="mr-0 leading-tight border-none px-1.5 py-0.5 text-[10px]">{MOCK_SUMMARY.failed}</Tag>
              </span>
            ),
            children: renderFailedCases()
          },
          {
            key: 'all',
            label: 'All Results',
            children: renderAllResults()
          },
          {
            key: 'artifacts',
            label: 'Artifacts',
            children: (
              <div className="grid grid-cols-4 gap-4">
                 {[1, 2, 3].map(i => (
                   <Card key={i} className="bg-slate-800/50 border-slate-700/50 hover:border-neon-cyan/50 cursor-pointer group transition-all">
                      <div className="flex flex-col items-center py-4 gap-2">
                         <FileText size={32} className="text-slate-500 group-hover:text-neon-cyan transition-colors" />
                         <span className="text-slate-300 text-sm">execution-log-{i}.txt</span>
                      </div>
                   </Card>
                 ))}
              </div>
            )
          }
        ]}
      />
    </div>
  );
};

export default TestRunReportDetail;

