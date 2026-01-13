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
const MOCK_JOBS: Job[] = [
  {
    id: 'job-1024',
    name: '端到端回归测试套件 A',
    triggeredBy: 'User',
    triggerUser: 'Zuolan',
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
    duration: '3m 12s',
  },
  {
    id: 'job-1022',
    name: '集成测试 - 支付',
    triggeredBy: 'API',
    environment: 'Dev',
    status: 'failed',
    startTime: dayjs().subtract(1, 'hour').toISOString(),
    endTime: dayjs().subtract(58, 'minute').toISOString(),
    duration: '2m 05s',
  },
  {
    id: 'job-1021',
    name: 'UI 视觉回归',
    triggeredBy: 'User',
    triggerUser: 'Admin',
    environment: 'Staging',
    status: 'passed',
    startTime: dayjs().subtract(3, 'hour').toISOString(),
    endTime: dayjs().subtract(2, 'hour').minute(55).toISOString(),
    duration: '5m 45s',
  },
  {
    id: 'job-1020',
    name: 'Nightly Build Check',
    triggeredBy: 'Cron',
    environment: 'Dev',
    status: 'passed',
    startTime: dayjs().subtract(1, 'day').toISOString(),
    duration: '12m 30s',
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
                   duration: '5m 00s' // mock
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
      case 'running': return <RefreshCw className="animate-spin text-blue-400" size={16} />;
      case 'passed': return <CheckCircle className="text-green-400" size={16} />;
      case 'failed': return <XCircle className="text-red-400" size={16} />;
      case 'queued': return <Clock className="text-yellow-400" size={16} />;
    }
  };

  const renderTriggerInfo = (job: Job) => {
    if (job.triggeredBy === 'User') {
      return (
        <span className="flex items-center gap-1 text-slate-400 text-xs">
          <User size={12} /> {job.triggerUser}
        </span>
      );
    }
    if (job.triggeredBy === 'Cron') {
      return (
        <span className="flex items-center gap-1 text-slate-400 text-xs">
          <Calendar size={12} /> Schedule
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1 text-slate-400 text-xs">
        <Terminal size={12} /> API
      </span>
    );
  };

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <Title level={2} className="text-slate-100 m-0 flex items-center gap-3">
            <Clock className="text-cyan-400" />
            Job Queue & History
          </Title>
          <Text className="text-slate-400">Monitor running tests and historical execution results.</Text>
        </div>
        <div className="flex gap-3">
           {/* Summary Stats could go here */}
           <div className="bg-slate-800/50 px-4 py-2 rounded-lg border border-slate-700/50 text-center">
              <div className="text-xs text-slate-400">Running</div>
              <div className="text-xl font-bold text-blue-400">{jobs.filter(j => j.status === 'running').length}</div>
           </div>
           <div className="bg-slate-800/50 px-4 py-2 rounded-lg border border-slate-700/50 text-center">
              <div className="text-xs text-slate-400">Failed (24h)</div>
              <div className="text-xl font-bold text-red-400">{jobs.filter(j => j.status === 'failed').length}</div>
           </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800 backdrop-blur-sm">
        <Timeline
            mode="left"
            items={jobs.map(job => ({
                color: job.status === 'running' ? 'blue' : job.status === 'failed' ? 'red' : 'green',
                dot: getStatusIcon(job.status),
                children: (
                    <Card 
                        className="bg-slate-800/50 border-slate-700/50 backdrop-blur-sm hover:border-indigo-500/50 transition-all mb-4"
                        bodyStyle={{ padding: '12px 16px' }}
                    >
                        <div className="flex flex-col gap-3">
                            {/* Top Row: Header Info */}
                            <div className="flex justify-between items-start">
                                <div className="space-y-1">
                                    <div className="flex items-center gap-2">
                                        <Text className="text-slate-200 font-medium text-lg">{job.name}</Text>
                                        <Tag color={job.environment === 'Prod' ? 'red' : 'blue'}>{job.environment}</Tag>
                                        <Text className="text-slate-500 text-xs">#{job.id}</Text>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <Text className="text-slate-400 text-xs flex items-center gap-1">
                                            {dayjs(job.startTime).fromNow()}
                                        </Text>
                                        {renderTriggerInfo(job)}
                                    </div>
                                </div>

                                <div className="text-right">
                                    <Badge status={getStatusColor(job.status)} text={<span className="capitalize text-slate-300">{job.status}</span>} />
                                    {job.duration && (
                                        <div className="text-xs text-slate-500 mt-1">
                                            Duration: {job.duration}
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Middle Row: Progress Bar (if running) */}
                            {job.status === 'running' && (
                                <div>
                                    <div className="flex justify-between text-xs text-slate-400 mb-1">
                                        <span>Executing test cases...</span>
                                        <span>{Math.round(job.progress || 0)}%</span>
                                    </div>
                                    <Progress 
                                        percent={job.progress} 
                                        status="active" 
                                        strokeColor={{ '0%': '#108ee9', '100%': '#87d068' }} 
                                        showInfo={false}
                                        size="small"
                                        trailColor="rgba(255,255,255,0.1)"
                                    />
                                </div>
                            )}

                            {/* Bottom Row: Logs Preview (Mock) */}
                            {job.status === 'failed' && (
                                <div className="bg-red-900/10 border border-red-900/30 p-2 rounded text-xs text-red-300 font-mono mt-2">
                                    Error: Assertion failed in Test_Payment_Gateway_Timeout. Expected 200 but got 504.
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


