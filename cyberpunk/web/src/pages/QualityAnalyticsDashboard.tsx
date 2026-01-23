import React from 'react';
import { Table, Tag, Tooltip, Card } from 'antd';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  ComposedChart,
  Bar
} from 'recharts';
import { Activity, AlertTriangle, TrendingUp, Shield, BarChart3 } from 'lucide-react';
import { motion } from 'framer-motion';

// const { Title, Text } = Typography; // Removed unused destructuring

// --- Mock Data ---

const TREND_DATA = [
  { date: '05-01', passRate: 92, duration: 240, total: 150 },
  { date: '05-02', passRate: 94, duration: 235, total: 152 },
  { date: '05-03', passRate: 88, duration: 260, total: 155 },
  { date: '05-04', passRate: 95, duration: 230, total: 158 },
  { date: '05-05', passRate: 96, duration: 225, total: 160 },
  { date: '05-06', passRate: 91, duration: 250, total: 162 },
  { date: '05-07', passRate: 98, duration: 220, total: 165 },
];

const FLAKY_TESTS = [
  { key: '1', name: '结账支付重试流程', failureRate: 15, lastFail: '2小时前', module: '支付' },
  { key: '2', name: '库存同步竞态条件', failureRate: 12, lastFail: '5小时前', module: '库存' },
  { key: '3', name: '用户资料大图上传', failureRate: 8, lastFail: '1天前', module: '用户' },
  { key: '4', name: '搜索 Elastic 重新索引延迟', failureRate: 6, lastFail: '3天前', module: '搜索' },
  { key: '5', name: '认证令牌刷新并发问题', failureRate: 5, lastFail: '4天前', module: '认证' },
];

const API_COVERAGE_MODULES = [
  { name: '认证', coverage: 95, endpoints: 12, critical: true },
  { name: '用户', coverage: 88, endpoints: 24, critical: true },
  { name: '支付', coverage: 92, endpoints: 18, critical: true },
  { name: '订单', coverage: 78, endpoints: 30, critical: true },
  { name: '产品', coverage: 85, endpoints: 45, critical: false },
  { name: '购物车', coverage: 90, endpoints: 8, critical: true },
  { name: '搜索', coverage: 65, endpoints: 15, critical: false },
  { name: '评论', coverage: 45, endpoints: 10, critical: false },
  { name: '管理', coverage: 70, endpoints: 50, critical: false },
  { name: '报表', coverage: 30, endpoints: 5, critical: false },
  { name: '通知', coverage: 82, endpoints: 14, critical: false },
  { name: '媒体', coverage: 60, endpoints: 20, critical: false },
];

interface TooltipPayload {
  name: string;
  value: number | string;
  color: string;
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: TooltipPayload[];
  label?: string;
}

// Custom Tooltip for Recharts
const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-slate-200 p-3 rounded shadow-lg">
        <p className="text-slate-500 mb-1 font-mono text-xs">{label}</p>
        {payload.map((entry: TooltipPayload, index: number) => (
          <p key={index} style={{ color: entry.color }} className="text-sm font-medium">
            {entry.name === 'Pass Rate' ? '通过率' : entry.name === 'Duration' ? '平均耗时' : entry.name === 'Total Tests' ? '测试总数' : entry.name}: {entry.value}
            {entry.name === 'Pass Rate' ? '%' : entry.name === 'Duration' ? '秒' : ''}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const QualityAnalyticsDashboard: React.FC = () => {

  const getCoverageColor = (coverage: number) => {
    if (coverage >= 90) return 'bg-emerald-50 border-emerald-200 text-emerald-600';
    if (coverage >= 75) return 'bg-blue-50 border-blue-200 text-blue-600';
    if (coverage >= 50) return 'bg-amber-50 border-amber-200 text-amber-600';
    return 'bg-red-50 border-red-200 text-red-600';
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6 max-w-7xl mx-auto p-6"
    >
      {/* Header */}
      <div className="flex justify-between items-center mb-2">
        <motion.div
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-bold text-slate-900 mb-1 flex items-center gap-3 tracking-tight">
            <Activity className="text-blue-600" />
            质量分析
          </h1>
          <p className="text-slate-500 text-sm">深入探索测试稳定性、性能以及覆盖率指标。</p>
        </motion.div>
        <motion.div
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="flex gap-2"
        >
          <Tag className="bg-white border-slate-200 text-slate-500 px-3 py-1 text-xs font-mono">过去 7 天</Tag>
        </motion.div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pass Rate Trend */}
        <Card title={<span className="text-slate-700 flex items-center gap-2 font-medium"><TrendingUp size={16} className="text-emerald-500" /> 通过率趋势</span>} bordered={false} className="shadow-sm">
          <div className="h-[300px] w-full pt-4" style={{ minHeight: '300px' }}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={TREND_DATA} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="date" stroke="#94a3b8" tick={{ fontSize: 12, fontFamily: 'monospace' }} />
                <YAxis stroke="#94a3b8" domain={[80, 100]} tick={{ fontSize: 12, fontFamily: 'monospace' }} />
                <RechartsTooltip content={<CustomTooltip />} />
                <Line
                  type="monotone"
                  dataKey="passRate"
                  name="Pass Rate"
                  stroke="#10b981"
                  strokeWidth={3}
                  dot={{ r: 4, fill: '#fff', stroke: '#10b981', strokeWidth: 2 }}
                  activeDot={{ r: 6, fill: '#10b981', stroke: '#fff', strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Duration Trend */}
        <Card title={<span className="text-slate-700 flex items-center gap-2 font-medium"><BarChart3 size={16} className="text-blue-500" /> 平均耗时趋势</span>} bordered={false} className="shadow-sm">
          <div className="h-[300px] w-full pt-4" style={{ minHeight: '300px' }}>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={TREND_DATA} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="date" stroke="#94a3b8" tick={{ fontSize: 12, fontFamily: 'monospace' }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 12, fontFamily: 'monospace' }} unit="s" />
                <RechartsTooltip content={<CustomTooltip />} />
                <Bar
                  dataKey="duration"
                  name="Duration"
                  fill="#3b82f6"
                  radius={[4, 4, 0, 0]}
                  barSize={30}
                  fillOpacity={0.8}
                />
                <Line type="monotone" dataKey="total" name="Total Tests" stroke="#64748b" dot={false} strokeDasharray="5 5" strokeWidth={2} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Flaky Tests */}
        <div className="lg:col-span-2">
          <Card className="h-full shadow-sm" bordered={false} title={<span className="text-slate-700 flex items-center gap-2 font-medium"><AlertTriangle size={16} className="text-amber-500" /> 稳定性较低的测试</span>}>
            <Table
              dataSource={FLAKY_TESTS}
              pagination={false}
              className="ant-table-clean"
              rowClassName="bg-transparent hover:bg-slate-50"
              columns={[
                {
                  title: '测试用例',
                  dataIndex: 'name',
                  key: 'name',
                  render: (text: string) => <span className="text-slate-700 font-medium text-sm">{text}</span>
                },
                {
                  title: '模块',
                  dataIndex: 'module',
                  key: 'module',
                  render: (text: string) => <Tag className="bg-slate-50 border-slate-200 text-slate-500 font-mono">{text}</Tag>
                },
                {
                  title: '失败率',
                  dataIndex: 'failureRate',
                  key: 'failureRate',
                  render: (rate: number) => (
                    <div className="flex items-center gap-2">
                      <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden w-24">
                        <div className="h-full bg-amber-500" style={{ width: `${rate}%` }}></div>
                      </div>
                      <span className="text-amber-600 font-bold text-xs font-mono">{rate}%</span>
                    </div>
                  )
                },
                {
                  title: '最近失败',
                  dataIndex: 'lastFail',
                  key: 'lastFail',
                  render: (text: string) => <span className="text-slate-400 text-xs font-mono">{text}</span>
                }
              ]}
            />
          </Card>
        </div>

        {/* API Coverage Heatmap */}
        <div className="lg:col-span-1">
          <Card className="h-full shadow-sm" bordered={false} title={<span className="text-slate-700 flex items-center gap-2 font-medium"><Shield size={16} className="text-blue-600" /> API 覆盖率图谱</span>}>
            <div className="grid grid-cols-2 gap-3">
              {API_COVERAGE_MODULES.map((mod, i) => (
                <Tooltip key={mod.name} title={`${mod.endpoints} 个端点 - 已覆盖 ${mod.coverage}%`}>
                  <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.5 + (i * 0.05) }}
                    className={`
                                p-3 rounded-lg border transition-all hover:shadow-md cursor-default
                                flex flex-col justify-between h-24
                                ${getCoverageColor(mod.coverage)}
                            `}>
                    <div className="flex justify-between items-start">
                      <span className="font-medium font-mono text-xs uppercase">{mod.name}</span>
                      {mod.critical && <Activity size={12} className="opacity-70" />}
                    </div>
                    <div>
                      <div className="text-2xl font-bold">{mod.coverage}%</div>
                      <div className="text-[10px] opacity-70 font-mono">{mod.endpoints} 端点</div>
                    </div>
                  </motion.div>
                </Tooltip>
              ))}
            </div>
            <div className="mt-4 flex gap-4 justify-center text-xs text-slate-500 font-mono">
              <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-500"></div> 高</span>
              <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-blue-500"></div> 良</span>
              <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-amber-500"></div> 中</span>
              <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500"></div> 低</span>
            </div>
          </Card>
        </div>
      </div>
    </motion.div>
  );
};

export default QualityAnalyticsDashboard;
