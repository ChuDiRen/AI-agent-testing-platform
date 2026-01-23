import React from 'react';
import { Button, Avatar } from 'antd';
import {
  Plus,
  FileText,
  Settings,
  Zap,
  GitCommit,
  Server,
  Database,
  Cpu,
  Activity,
  Bot,
  Clock
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer
} from 'recharts';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';

// --- Mock Data ---

const activityLog = [
  { id: 1, user: 'Alex Chen', action: '更新了 swagger.json', time: '10分钟前', avatar: 'https://i.pravatar.cc/150?u=me' },
  { id: 2, user: 'Sarah Connor', action: '修复了测试 #102', time: '45分钟前', avatar: 'https://i.pravatar.cc/150?u=5' },
  { id: 3, user: 'System', action: '发布了 v2.4.1', time: '2小时前', avatar: null },
  { id: 4, user: 'Mike Ross', action: '创建了新智能体', time: '5小时前', avatar: 'https://i.pravatar.cc/150?u=7' },
];

const quotaData = [
  { name: '已用', value: 75, color: '#2563EB' }, // Blue 600
  { name: '剩余', value: 25, color: '#E2E8F0' }, // Slate 200
];

const storageData = [
  { name: '已用', value: 42, color: '#7C3AED' }, // Violet 600
  { name: '空闲', value: 58, color: '#E2E8F0' }, // Slate 200
];

// --- Components ---

const StatusDot = ({ status }: { status: 'healthy' | 'warning' | 'error' }) => {
  const colors = {
    healthy: 'bg-green-500',
    warning: 'bg-amber-500',
    error: 'bg-red-500'
  };

  return (
    <div className="relative flex items-center justify-center w-2.5 h-2.5">
      <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping ${colors[status]}`} />
      <span className={`relative inline-flex rounded-full h-2 w-2 ${colors[status]}`} />
    </div>
  );
};

export const HomeOverview: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Welcome Banner */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="rounded-xl border border-border bg-white p-6 shadow-sm mb-8"
      >
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 mb-1 tracking-tight">
              早上好，Alex。
            </h1>
            <div className="flex items-center gap-3 text-slate-500 text-sm">
              <StatusDot status="healthy" />
              <span className="font-medium">系统在线 — v2.4.1</span>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <Button
              type="primary"
              icon={<Plus size={16} />}
              className="bg-primary hover:bg-blue-700 h-9"
            >
              新建测试
            </Button>
            <Button
              className="hover:border-primary hover:text-primary transition-colors h-9"
              icon={<FileText size={16} />}
            >
              报告
            </Button>
            <Button
              className="hover:border-primary hover:text-primary transition-colors h-9"
              icon={<Settings size={16} />}
            >
              API 配置
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Recent Activity - Takes up 2 columns */}
        <div className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-lg font-semibold flex items-center gap-2">
                <Activity size={20} className="text-slate-400" />
                近期活动
              </CardTitle>
              <Button type="link" size="small" className="text-primary hover:text-blue-700">查看全部</Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {activityLog.map((log) => (
                  <div
                    key={log.id}
                    className="flex gap-4 py-2 hover:bg-slate-50 rounded-lg px-2 transition-colors -mx-2 cursor-pointer items-start"
                  >
                    <div className="flex-shrink-0 mt-1">
                      {log.avatar ? (
                        <Avatar src={log.avatar} size={32} className="border border-slate-200" />
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-500">
                          <Bot size={16} />
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-700">
                        <span className="font-semibold text-slate-900">{log.user}</span> {log.action}
                      </p>
                      <div className="text-xs text-slate-400 mt-1 flex items-center gap-2">
                        <Clock size={12} />
                        {log.time}
                      </div>
                    </div>
                    <div className="flex items-center text-slate-300">
                      <GitCommit size={14} />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column Stack */}
        <div className="flex flex-col gap-6">

          {/* Resource Usage */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-semibold flex items-center gap-2">
                <Cpu size={20} className="text-slate-400" />
                资源使用
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-around py-4">
                {/* API Usage */}
                <div className="relative w-24 h-24 flex items-center justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={quotaData}
                        innerRadius={36}
                        outerRadius={44}
                        startAngle={90}
                        endAngle={-270}
                        dataKey="value"
                        stroke="none"
                      >
                        {quotaData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                    <span className="text-lg font-bold text-slate-900">75%</span>
                    <span className="text-[10px] text-slate-400 uppercase font-medium">API</span>
                  </div>
                </div>

                {/* Storage Usage */}
                <div className="relative w-24 h-24 flex items-center justify-center">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={storageData}
                        innerRadius={36}
                        outerRadius={44}
                        startAngle={90}
                        endAngle={-270}
                        dataKey="value"
                        stroke="none"
                      >
                        {storageData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
                    <span className="text-lg font-bold text-slate-900">42%</span>
                    <span className="text-[10px] text-slate-400 uppercase font-medium">存储</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* System Health */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-semibold flex items-center gap-2">
                <Server size={20} className="text-slate-400" />
                系统状态
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
                  <div className="flex items-center gap-3">
                    <div className="p-1.5 bg-blue-100 rounded text-primary">
                      <Database size={14} />
                    </div>
                    <span className="text-sm font-medium text-slate-700">RAG 服务</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500 font-mono">14ms</span>
                    <StatusDot status="healthy" />
                  </div>
                </div>

                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
                  <div className="flex items-center gap-3">
                    <div className="p-1.5 bg-purple-100 rounded text-purple-600">
                      <Zap size={14} />
                    </div>
                    <span className="text-sm font-medium text-slate-700">执行服务</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500 font-mono">230ms</span>
                    <StatusDot status="healthy" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

        </div>
      </div>
    </div>
  );
};
