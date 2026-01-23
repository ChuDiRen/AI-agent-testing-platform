import React, { useState, useEffect } from 'react';
import { Card, Badge, Progress, Tag, Timeline, Typography } from 'antd';
import { Clock, CheckCircle, XCircle, User, Calendar, Terminal, RefreshCw } from 'lucide-react';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';

dayjs.extend(relativeTime);

const { Title, Text } = Typography;

// --- Types ---
interface Job {
  id: string;
  name: string;
  triggeredBy: 'User' | 'Cron' | 'API';
  triggerUser?: string;
  environment: 'Dev' | 'Staging' | 'Prod';
  status: 'running' | 'passed' | 'failed' | 'queued';
  startTime: string; // ISO string
  endTime?: string;
  duration?: string;
  progress?: number; // 0-100
}

// --- Mock Data ---
// --- Mock Data ---
const MOCK_JOBS: Job[] = [
  {
    id: 'job-1024',
    name: '端到端回归测试套件 A',
    triggeredBy: 'User',
    triggerUser: 'Alex Chen',
    environment: 'Staging',
    status: 'running',
    startTime: dayjs().subtract(2, 'minute').toISOString(),
    progress: 45,
  },
  {
    id: 'job-1023',
    name: '冒烟测试 - API V2',
    triggeredBy: 'Cron',
    environment: 'Prod',
    status: 'passed',
    startTime: dayjs().subtract(15, 'minute').toISOString(),
    endTime: dayjs().subtract(12, 'minute').toISOString(),
    duration: '3分 12秒',
  },
  {
    id: 'job-1022',
    name: '集成测试 - 支付模块',
    triggeredBy: 'API',
    environment: 'Dev',
    status: 'failed',
    startTime: dayjs().subtract(1, 'hour').toISOString(),
    endTime: dayjs().subtract(58, 'minute').toISOString(),
    duration: '2分 05秒',
  },
  {
    id: 'job-1021',
    name: 'UI 视觉回归测试',
    triggeredBy: 'User',
    triggerUser: 'Admin',
    environment: 'Staging',
    status: 'passed',
    startTime: dayjs().subtract(3, 'hour').toISOString(),
    endTime: dayjs().subtract(2, 'hour').minute(55).toISOString(),
    duration: '5分 45秒',
  },
  {
    id: 'job-1020',
    name: '每晚构建检查',
    triggeredBy: 'Cron',
    environment: 'Dev',
    status: 'passed',
    startTime: dayjs().subtract(1, 'day').toISOString(),
    duration: '12分 30秒',
  },
];

export const JobQueueHistory: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>(MOCK_JOBS);

  // Simulate progress for running jobs
  useEffect(() => {
    const interval = setInterval(() => {
      setJobs((prevJobs) =>
        prevJobs.map((job) => {
          if (job.status === 'running' && job.progress !== undefined && job.progress < 100) {
            const increment = Math.random() * 5;
            const newProgress = Math.min(100, job.progress + increment);

            // If finished (simulation)
            if (newProgress >= 100) {
              return {
                ...job,
                status: 'passed',
                progress: 100,
                endTime: dayjs().toISOString(),
                duration: '5分 00秒' // mock
              }
            }
            return { ...job, progress: newProgress };
          }
          return job;
        })
      );
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: Job['status']) => {
    switch (status) {
      case 'running': return 'processing';
      case 'passed': return 'success';
      case 'failed': return 'error';
      case 'queued': return 'warning';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: Job['status']) => {
    switch (status) {
      case 'running': return <RefreshCw className="animate-spin text-blue-500" size={16} />;
      case 'passed': return <CheckCircle className="text-emerald-500" size={16} />;
      case 'failed': return <XCircle className="text-red-500" size={16} />;
      case 'queued': return <Clock className="text-amber-500" size={16} />;
    }
  };

  const renderTriggerInfo = (job: Job) => {
    if (job.triggeredBy === 'User') {
      return (
        <span className="flex items-center gap-1 text-slate-500 text-xs">
          <User size={12} /> {job.triggerUser}
        </span>
      );
    }
    if (job.triggeredBy === 'Cron') {
      return (
        <span className="flex items-center gap-1 text-slate-500 text-xs">
          <Calendar size={12} /> 定时任务
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1 text-slate-500 text-xs">
        <Terminal size={12} /> API
      </span>
    );
  };

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <Title level={2} className="text-slate-900 m-0 flex items-center gap-3">
            <Clock className="text-blue-600" />
            任务队列 & 历史
          </Title>
          <Text className="text-slate-500">监控正在运行的测试和历史执行结果。</Text>
        </div>
        <div className="flex gap-3">
          {/* Summary Stats */}
          <div className="bg-white px-4 py-2 rounded-lg border border-slate-200 text-center shadow-sm">
            <div className="text-xs text-slate-500">运行中</div>
            <div className="text-xl font-bold text-blue-600">{jobs.filter(j => j.status === 'running').length}</div>
          </div>
          <div className="bg-white px-4 py-2 rounded-lg border border-slate-200 text-center shadow-sm">
            <div className="text-xs text-slate-500">失败 (24h)</div>
            <div className="text-xl font-bold text-red-500">{jobs.filter(j => j.status === 'failed').length}</div>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-white p-8 rounded-xl border border-slate-200 shadow-sm">
        <Timeline
          mode="left"
          items={jobs.map(job => ({
            color: job.status === 'running' ? '#3b82f6' : job.status === 'failed' ? '#ef4444' : '#10b981',
            dot: getStatusIcon(job.status),
            children: (
              <Card
                className="border-slate-200 hover:border-blue-300 hover:shadow-md transition-all mb-4"
                styles={{ body: { padding: '16px' } }}
              >
                <div className="flex flex-col gap-3">
                  {/* Top Row: Header Info */}
                  <div className="flex justify-between items-start">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Text className="text-slate-800 font-medium text-lg">{job.name}</Text>
                        <Tag color={job.environment === 'Prod' ? 'red' : 'blue'}>{job.environment}</Tag>
                        <Text className="text-slate-400 text-xs">#{job.id}</Text>
                      </div>
                      <div className="flex items-center gap-4">
                        <Text className="text-slate-500 text-xs flex items-center gap-1">
                          {dayjs(job.startTime).fromNow()}
                        </Text>
                        {renderTriggerInfo(job)}
                      </div>
                    </div>

                    <div className="text-right">
                      <Badge status={getStatusColor(job.status)} text={<span className="capitalize text-slate-600">{job.status}</span>} />
                      {job.duration && (
                        <div className="text-xs text-slate-400 mt-1">
                          耗时: {job.duration}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Middle Row: Progress Bar (if running) */}
                  {job.status === 'running' && (
                    <div>
                      <div className="flex justify-between text-xs text-slate-500 mb-1">
                        <span>正在执行测试用例...</span>
                        <span>{Math.round(job.progress || 0)}%</span>
                      </div>
                      <Progress
                        percent={job.progress}
                        status="active"
                        strokeColor={{ '0%': '#3b82f6', '100%': '#22c55e' }}
                        showInfo={false}
                        size="small"
                      />
                    </div>
                  )}

                  {/* Bottom Row: Logs Preview (Mock) */}
                  {job.status === 'failed' && (
                    <div className="bg-red-50 border border-red-100 p-3 rounded-md text-xs text-red-600 font-mono mt-2">
                      错误: Test_Payment_Gateway_Timeout 发生断言失败。预期 200 但得到 504。
                    </div>
                  )}
                </div>
              </Card>
            )
          }))}
        />
      </div>
    </div>
  );
};
