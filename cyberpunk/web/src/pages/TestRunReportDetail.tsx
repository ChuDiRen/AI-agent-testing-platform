import React, { useState } from 'react';
import { Card, Tabs, Collapse, Tag, Typography, Button, Alert, Image, Progress, Statistic } from 'antd';
import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend
} from 'recharts';
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
  name: '端到端支付网关校验 (E2E)',
  startTime: '2025-05-14 10:30:00',
  duration: '4分 12秒',
  total: 45,
  passed: 42,
  failed: 2,
  skipped: 1,
  environment: '测试环境'
};

const MOCK_FAILED_CASES: TestCase[] = [
  {
    id: 'tc-101',
    name: '验证信用卡支付流程',
    suite: '结帐模块',
    status: 'failed',
    duration: '12秒',
    error: {
      message: 'AssertionError: 预期支付状态为 "Completed" 但实际为 "Failed"',
      stackTrace: `Error: Expected payment status to be "Completed" but got "Failed"
    at PaymentPage.verifyStatus (src/pages/payment.page.ts:45:12)
    at async TestRunner.execute (src/runner/core.ts:120:5)
    at async Suite.run (src/runner/suite.ts:34:9)`
    },
    screenshotUrl: 'https://placehold.co/600x400/f8fafc/ef4444?text=Payment+Failure+Screenshot',
    aiAnalysis: '支付网关返回了“失败”状态。根据日志分析，模拟服务器响应了 402 Payment Required 错误，这表明测试用的信用卡卡号（末尾为 4242）在测试环境中可能被配置为触发拒绝。建议：检查测试环境的测试数据配置。'
  },
  {
    id: 'tc-102',
    name: '检查库存预留功能',
    suite: '库存模块',
    status: 'failed',
    duration: '5秒',
    error: {
      message: 'TimeoutError: 在 5000ms 内未找到元素 ".stock-badge"',
      stackTrace: `TimeoutError: Element ".stock-badge" not found after 5000ms
    at InventoryPage.checkBadge (src/pages/inventory.page.ts:22:8)
    at async Context.<anonymous> (src/tests/inventory.spec.ts:15:3)`
    },
    aiAnalysis: '元素 ".stock-badge" 未出现。这通常发生在页面加载速度慢于预期，或者产品实际已售罄的情况下。网络日志显示库存 API 返回了 200 OK，但响应体中 "quantity: 0"。而测试脚本预期 "quantity > 0"。'
  }
];

const MOCK_PASSED_CASES: TestCase[] = Array(10).fill(null).map((_, i) => ({
  id: `tc-20${i}`,
  name: `成功测试用例 #${i + 1}`,
  suite: '通用模块',
  status: 'passed',
  duration: `${Math.floor(Math.random() * 500) + 100}ms`
}));

const PIE_DATA = [
  { name: '通过', value: MOCK_SUMMARY.passed, color: '#10b981' },
  { name: '失败', value: MOCK_SUMMARY.failed, color: '#ef4444' },
  { name: '跳过', value: MOCK_SUMMARY.skipped, color: '#64748b' },
];

const MODULE_PERFORMANCE_DATA = [
  { name: '认证', passed: 15, failed: 0, duration: 120 },
  { name: '结帐', passed: 8, failed: 1, duration: 450 },
  { name: '库存', passed: 10, failed: 1, duration: 300 },
  { name: '用户', passed: 9, failed: 0, duration: 150 },
];

const TestRunReportDetail: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const renderOverview = () => (
    <div className="bg-white p-6 rounded-b-lg border border-slate-200 border-t-0 space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="h-[300px]">
          <h4 className="text-slate-700 font-medium mb-4 flex items-center gap-2">
            结果分布
          </h4>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={PIE_DATA}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {PIE_DATA.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <RechartsTooltip />
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="h-[300px]">
          <h4 className="text-slate-700 font-medium mb-4 flex items-center gap-2">
            模块性能
          </h4>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={MODULE_PERFORMANCE_DATA} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={80} tick={{ fontSize: 12 }} />
              <RechartsTooltip />
              <Legend />
              <Bar dataKey="passed" stackId="a" fill="#10b981" name="通过" />
              <Bar dataKey="failed" stackId="a" fill="#ef4444" name="失败" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );

  const renderScorecard = () => (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <Card bordered={false} className="shadow-sm">
        <Statistic
          title={<span className="text-slate-500 text-xs uppercase tracking-wider">通过率</span>}
          value={((MOCK_SUMMARY.passed / MOCK_SUMMARY.total) * 100).toFixed(1)}
          suffix="%"
          valueStyle={{ color: '#10b981', fontWeight: 'bold' }}
          prefix={<CheckCircle size={20} />}
        />
        <Progress percent={Math.round((MOCK_SUMMARY.passed / MOCK_SUMMARY.total) * 100)} showInfo={false} strokeColor="#10b981" trailColor="#f1f5f9" size="small" className="mt-2" />
      </Card>

      <Card bordered={false} className="shadow-sm">
        <Statistic
          title={<span className="text-slate-500 text-xs uppercase tracking-wider">总工作耗时</span>}
          value={MOCK_SUMMARY.duration}
          valueStyle={{ color: '#1e293b' }}
          prefix={<Clock size={20} className="text-blue-500" />}
        />
        <div className="text-xs text-slate-400 mt-2">平均每条用例 120ms</div>
      </Card>

      <Card bordered={false} className="shadow-sm">
        <Statistic
          title={<span className="text-slate-500 text-xs uppercase tracking-wider">开始时间</span>}
          value={MOCK_SUMMARY.startTime}
          valueStyle={{ color: '#1e293b', fontSize: '1.2rem' }}
          prefix={<Calendar size={20} className="text-purple-500" />}
        />
        <div className="text-xs text-slate-400 mt-2">{MOCK_SUMMARY.environment}</div>
      </Card>

      <Card bordered={false} className="shadow-sm">
        <div className="flex flex-col h-full justify-between">
          <span className="text-slate-500 text-xs uppercase tracking-wider">结果摘要</span>
          <div className="flex gap-2 mt-2">
            <div className="flex-1 bg-green-50 border border-green-100 rounded p-2 text-center">
              <div className="text-green-600 font-bold text-lg">{MOCK_SUMMARY.passed}</div>
              <div className="text-[10px] text-green-600/70 uppercase">已通过</div>
            </div>
            <div className="flex-1 bg-red-50 border border-red-100 rounded p-2 text-center">
              <div className="text-red-600 font-bold text-lg">{MOCK_SUMMARY.failed}</div>
              <div className="text-[10px] text-red-600/70 uppercase">已失败</div>
            </div>
            <div className="flex-1 bg-slate-50 border border-slate-100 rounded p-2 text-center">
              <div className="text-slate-600 font-bold text-lg">{MOCK_SUMMARY.skipped}</div>
              <div className="text-[10px] text-slate-500/70 uppercase">跳过</div>
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
      expandIcon={({ isActive }) => <ChevronRight size={16} className={`text-slate-400 transition-transform ${isActive ? 'rotate-90' : ''}`} />}
      items={MOCK_FAILED_CASES.map(testCase => ({
        key: testCase.id,
        label: (
          <div className="flex items-center gap-3 py-1">
            <XCircle className="text-red-500" size={18} />
            <span className="text-slate-800 font-medium text-base">{testCase.name}</span>
            <Tag className="bg-slate-100 border-slate-200 text-slate-500 ml-auto">{testCase.suite}</Tag>
            <span className="text-slate-400 text-xs font-mono">{testCase.duration}</span>
          </div>
        ),
        className: "bg-white border border-red-100 rounded-lg mb-4 !overflow-hidden shadow-sm",
        style: { borderBottom: '1px solid #fee2e2' },
        children: (
          <div className="flex flex-col gap-4 p-2">
            {/* Error Message */}
            <Alert
              title={<span className="font-mono font-bold text-red-700">错误详情</span>}
              description={<span className="font-mono text-red-600">{testCase.error?.message}</span>}
              type="error"
              showIcon
              className="bg-red-50 border-red-100"
            />

            {/* AI Analysis */}
            {testCase.aiAnalysis && (
              <div className="bg-blue-50 border border-blue-100 rounded-lg p-4 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
                <div className="flex gap-3">
                  <Bot className="text-blue-500 shrink-0 mt-1" size={20} />
                  <div>
                    <h4 className="text-blue-700 font-medium mb-1">AI 根本原因分析</h4>
                    <p className="text-slate-600 text-sm leading-relaxed">
                      {testCase.aiAnalysis}
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="flex gap-6 mt-2">
              {/* Stack Trace */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2 text-slate-500 text-sm">
                  <Terminal size={14} /> 堆栈追踪 (Stack Trace)
                </div>
                <div className="rounded-lg overflow-hidden border border-slate-200 shadow-sm">
                  <SyntaxHighlighter
                    language="typescript"
                    style={vscDarkPlus}
                    customStyle={{ margin: 0, padding: '1rem', fontSize: '12px', background: '#1e293b' }}
                  >
                    {testCase.error?.stackTrace || ''}
                  </SyntaxHighlighter>
                </div>
              </div>

              {/* Screenshot */}
              {testCase.screenshotUrl && (
                <div className="w-80 shrink-0">
                  <div className="flex items-center gap-2 mb-2 text-slate-500 text-sm">
                    <ImageIcon size={14} /> 失败截图
                  </div>
                  <Image
                    src={testCase.screenshotUrl}
                    className="rounded-lg border border-slate-200"
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
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-sm">
      {MOCK_PASSED_CASES.map((tc, idx) => (
        <div key={tc.id} className={`flex items-center justify-between p-4 ${idx !== MOCK_PASSED_CASES.length - 1 ? 'border-b border-slate-100' : ''} hover:bg-slate-50 transition-colors`}>
          <div className="flex items-center gap-3">
            <CheckCircle className="text-emerald-500" size={16} />
            <span className="text-slate-700">{tc.name}</span>
          </div>
          <div className="flex items-center gap-4">
            <Tag className="bg-slate-100 border-slate-200 text-slate-500 m-0">{tc.suite}</Tag>
            <span className="text-slate-400 font-mono text-xs w-16 text-right">{tc.duration}</span>
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="animate-fade-in space-y-6 max-w-7xl mx-auto p-6">
      <div className="flex justify-between items-start">
        <div>
          <Title level={2} className="!text-slate-900 !mb-1">{MOCK_SUMMARY.name}</Title>
          <Text className="text-slate-500">运行 ID: #{MOCK_SUMMARY.id} • {MOCK_SUMMARY.startTime}</Text>
        </div>
        <div className="flex gap-2">
          <Button icon={<Download size={16} />} className="text-slate-600 border-slate-300 hover:text-blue-600 hover:border-blue-400">导出报告</Button>
          <Button type="primary">重测失败项</Button>
        </div>
      </div>

      {renderScorecard()}

      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        type="card"
        items={[
          {
            key: 'overview',
            label: '概览',
            children: renderOverview()
          },
          {
            key: 'failed',
            label: (
              <span className="flex items-center gap-2">
                失败用例
                <Tag color="#ef4444" className="mr-0 leading-tight border-none px-1.5 py-0.5 text-[10px]">{MOCK_SUMMARY.failed}</Tag>
              </span>
            ),
            children: renderFailedCases()
          },
          {
            key: 'all',
            label: '所有结果',
            children: renderAllResults()
          },
          {
            key: 'artifacts',
            label: '运行产物',
            children: (
              <div className="grid grid-cols-4 gap-4 bg-white p-4 border border-t-0 border-slate-200 rounded-b-lg">
                {[1, 2, 3].map(i => (
                  <Card bordered={false} key={i} className="bg-slate-50 border border-slate-200 hover:border-blue-300 cursor-pointer group transition-all shadow-sm">
                    <div className="flex flex-col items-center py-4 gap-2">
                      <FileText size={32} className="text-slate-400 group-hover:text-blue-500 transition-colors" />
                      <span className="text-slate-600 text-sm">execution-log-{i}.txt</span>
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
