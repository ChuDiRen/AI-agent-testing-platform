import React from 'react';
import { Card, Table, Typography, Tag, Tooltip } from 'antd';
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

const { Title, Text } = Typography;

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
  { key: '1', name: '结账支付重试流程', failureRate: 15, lastFail: '2 小时前', module: '支付' },
  { key: '2', name: '库存股票同步竞争条件', failureRate: 12, lastFail: '5 小时前', module: '库存' },
  { key: '3', name: '用户配置文件图片上传大文件', failureRate: 8, lastFail: '1 天前', module: '用户' },
  { key: '4', name: '搜索 Elasticsearch 重建索引延迟', failureRate: 6, lastFail: '3 天前', module: '搜索' },
  { key: '5', name: '认证令牌刷新并发', failureRate: 5, lastFail: '4 天前', module: '认证' },
];

const API_COVERAGE_MODULES = [
  { name: 'Auth', coverage: 95, endpoints: 12, critical: true },
  { name: 'User', coverage: 88, endpoints: 24, critical: true },
  { name: 'Payment', coverage: 92, endpoints: 18, critical: true },
  { name: 'Order', coverage: 78, endpoints: 30, critical: true },
  { name: 'Product', coverage: 85, endpoints: 45, critical: false },
  { name: 'Cart', coverage: 90, endpoints: 8, critical: true },
  { name: 'Search', coverage: 65, endpoints: 15, critical: false },
  { name: 'Review', coverage: 45, endpoints: 10, critical: false },
  { name: 'Admin', coverage: 70, endpoints: 50, critical: false },
  { name: 'Report', coverage: 30, endpoints: 5, critical: false },
  { name: 'Notif', coverage: 82, endpoints: 14, critical: false },
  { name: 'Media', coverage: 60, endpoints: 20, critical: false },
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
      <div className="bg-slate-900 border border-slate-700 p-3 rounded shadow-xl backdrop-blur-md">
        <p className="text-slate-300 mb-1 font-mono text-xs">{label}</p>
        {payload.map((entry: TooltipPayload, index: number) => (
          <p key={index} style={{ color: entry.color }} className="text-sm font-medium">
            {entry.name}: {entry.value}
            {entry.name === 'Pass Rate' ? '%' : entry.name === 'Duration' ? 's' : ''}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const QualityAnalyticsDashboard: React.FC = () => {

  const getCoverageColor = (coverage: number) => {
    if (coverage >= 90) return 'bg-green-500/20 border-green-500/50 text-green-400';
    if (coverage >= 75) return 'bg-blue-500/20 border-blue-500/50 text-blue-400';
    if (coverage >= 50) return 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400';
    return 'bg-red-500/20 border-red-500/50 text-red-400';
  };

  return (
    <div className="animate-fade-in space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-2">
        <div>
          <Title level={2} className="!text-slate-100 !mb-1 flex items-center gap-3">
            <Activity className="text-indigo-400" />
            Quality Analytics
          </Title>
          <Text className="text-slate-400">Deep dive into test stability, performance, and coverage metrics.</Text>
        </div>
        <div className="flex gap-2">
            <Tag className="bg-slate-800 border-slate-700 text-slate-300 px-3 py-1">Last 7 Days</Tag>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pass Rate Trend */}
        <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm" title={<span className="text-slate-200 flex items-center gap-2"><TrendingUp size={16} /> Pass Rate Trend</span>}>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={TREND_DATA} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 12 }} />
                <YAxis stroke="#64748b" domain={[80, 100]} tick={{ fontSize: 12 }} />
                <RechartsTooltip content={<CustomTooltip />} />
                <Line 
                  type="monotone" 
                  dataKey="passRate" 
                  name="Pass Rate" 
                  stroke="#4ade80" 
                  strokeWidth={3} 
                  dot={{ r: 4, fill: '#0f172a', stroke: '#4ade80', strokeWidth: 2 }} 
                  activeDot={{ r: 6, fill: '#4ade80' }} 
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Duration Trend */}
        <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm" title={<span className="text-slate-200 flex items-center gap-2"><BarChart3 size={16} /> Avg. Duration Trend</span>}>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={TREND_DATA} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 12 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 12 }} unit="s" />
                <RechartsTooltip content={<CustomTooltip />} />
                <Bar 
                  dataKey="duration" 
                  name="Duration" 
                  fill="#6366f1" 
                  radius={[4, 4, 0, 0]} 
                  barSize={30}
                  fillOpacity={0.6}
                />
                <Line type="monotone" dataKey="total" name="Total Tests" stroke="#94a3b8" dot={false} strokeDasharray="5 5" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Flaky Tests */}
        <div className="lg:col-span-2">
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm h-full" title={<span className="text-slate-200 flex items-center gap-2"><AlertTriangle size={16} className="text-yellow-400" /> Top Flaky Tests</span>}>
                <Table 
                    dataSource={FLAKY_TESTS} 
                    pagination={false} 
                    className="cyberpunk-table"
                    rowClassName="bg-transparent hover:bg-slate-800/30"
                    columns={[
                        { 
                            title: 'Test Case', 
                            dataIndex: 'name', 
                            key: 'name',
                            render: (text: string) => <span className="text-slate-300 font-mono text-sm">{text}</span>
                        },
                        { 
                            title: 'Module', 
                            dataIndex: 'module', 
                            key: 'module',
                            render: (text: string) => <Tag className="bg-slate-800 border-slate-700 text-slate-400">{text}</Tag>
                        },
                        { 
                            title: 'Failure Rate', 
                            dataIndex: 'failureRate', 
                            key: 'failureRate',
                            render: (rate: number) => (
                                <div className="flex items-center gap-2">
                                    <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden w-24">
                                        <div className="h-full bg-yellow-500" style={{ width: `${rate}%` }}></div>
                                    </div>
                                    <span className="text-yellow-500 font-bold text-xs">{rate}%</span>
                                </div>
                            )
                        },
                        { 
                            title: 'Last Fail', 
                            dataIndex: 'lastFail', 
                            key: 'lastFail',
                            render: (text: string) => <span className="text-slate-500 text-xs">{text}</span>
                        }
                    ]}
                />
            </Card>
        </div>

        {/* API Coverage Heatmap */}
        <div className="lg:col-span-1">
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm h-full" title={<span className="text-slate-200 flex items-center gap-2"><Shield size={16} className="text-blue-400" /> API Coverage Map</span>}>
                <div className="grid grid-cols-2 gap-3">
                    {API_COVERAGE_MODULES.map((mod) => (
                        <Tooltip key={mod.name} title={`${mod.endpoints} Endpoints - ${mod.coverage}% Covered`}>
                            <div className={`
                                p-3 rounded-lg border backdrop-blur-sm transition-all hover:scale-[1.02] cursor-default
                                flex flex-col justify-between h-24
                                ${getCoverageColor(mod.coverage)}
                            `}>
                                <div className="flex justify-between items-start">
                                    <span className="font-medium">{mod.name}</span>
                                    {mod.critical && <Activity size={12} className="opacity-70" />}
                                </div>
                                <div>
                                    <div className="text-2xl font-bold">{mod.coverage}%</div>
                                    <div className="text-[10px] opacity-70">{mod.endpoints} Endpoints</div>
                                </div>
                            </div>
                        </Tooltip>
                    ))}
                </div>
                <div className="mt-4 flex gap-4 justify-center text-xs text-slate-500">
                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-green-500"></div> High</span>
                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-blue-500"></div> Good</span>
                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-yellow-500"></div> Med</span>
                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500"></div> Low</span>
                </div>
            </Card>
        </div>
      </div>
    </div>
  );
};

export default QualityAnalyticsDashboard;
