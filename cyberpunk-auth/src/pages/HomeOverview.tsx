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
  Bot
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer
} from 'recharts';

// --- Mock Data ---

const activityLog = [
  { id: 1, user: 'Alex Chen', action: 'updated swagger.json', time: '10m ago', avatar: 'https://i.pravatar.cc/150?u=me' },
  { id: 2, user: 'Sarah Connor', action: 'fixed Test #102', time: '45m ago', avatar: 'https://i.pravatar.cc/150?u=5' },
  { id: 3, user: 'System', action: 'deployed v2.4.1', time: '2h ago', avatar: null },
  { id: 4, user: 'Mike Ross', action: 'created new agent', time: '5h ago', avatar: 'https://i.pravatar.cc/150?u=7' },
];

const quotaData = [
  { name: 'Used', value: 75, color: '#6366f1' }, // Indigo-500
  { name: 'Remaining', value: 25, color: '#1e293b' }, // Slate-800
];

const storageData = [
  { name: 'Used', value: 42, color: '#22d3ee' }, // Cyan-400
  { name: 'Free', value: 58, color: '#1e293b' }, // Slate-800
];

// --- Components ---

interface BentoCardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  icon?: React.ElementType;
  extra?: React.ReactNode;
}

const BentoCard: React.FC<BentoCardProps> = ({ children, className = "", title, icon: Icon, extra }) => (
  <div className={`bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-xl p-6 flex flex-col ${className}`}>
    {(title || Icon) && (
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2 text-slate-100 font-medium">
          {Icon && <Icon size={18} className="text-indigo-400" />}
          {title}
        </div>
        {extra}
      </div>
    )}
    <div className="flex-1 min-h-0 relative">
      {children}
    </div>
  </div>
);

const StatusDot = ({ status }: { status: 'healthy' | 'warning' | 'error' }) => {
  const colors = {
    healthy: 'bg-green-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500'
  };
  
  return (
    <div className="relative flex items-center justify-center w-3 h-3">
      <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping ${colors[status]}`} />
      <span className={`relative inline-flex rounded-full h-2 w-2 ${colors[status]}`} />
    </div>
  );
};

export const HomeOverview: React.FC = () => {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome Banner */}
      <div className="relative rounded-2xl overflow-hidden border border-slate-800 bg-slate-900">
        <div className="absolute inset-0 bg-gradient-to-r from-indigo-900/20 to-cyan-900/20" />
        <div className="relative p-8 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2 font-sans tracking-tight">
              早上好，Alex。
            </h1>
            <div className="flex items-center gap-2 text-slate-400">
              <StatusDot status="healthy" />
              <span className="font-mono text-sm">所有系统正常运行</span>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-3">
            <Button 
              type="primary" 
              icon={<Plus size={16} />}
              className="!bg-indigo-600 hover:!bg-indigo-500 !border-0 !h-10 !px-6 !font-medium"
            >
              新建测试
            </Button>
            <Button 
              className="!bg-slate-800 !border-slate-700 hover:!border-slate-600 !text-slate-200 !h-10"
              icon={<FileText size={16} />}
            >
              查看报告
            </Button>
            <Button 
              className="!bg-slate-800 !border-slate-700 hover:!border-slate-600 !text-slate-200 !h-10"
              icon={<Settings size={16} />}
            >
              配置 API
            </Button>
          </div>
        </div>
      </div>

      {/* Bento Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-auto md:h-[400px]">
        
        {/* Recent Activity - Takes up 2 columns */}
        <BentoCard 
          title="最近活动" 
          icon={Activity} 
          className="md:col-span-2 overflow-hidden"
          extra={<Button type="link" size="small" className="!text-indigo-400">查看全部</Button>}
        >
          <div className="space-y-0 relative">
             {/* Timeline Line */}
             <div className="absolute left-[19px] top-2 bottom-4 w-[2px] bg-slate-800 z-0" />
             
             {activityLog.map((log) => (
               <div key={log.id} className="relative z-10 flex gap-4 py-3 group hover:bg-slate-800/30 rounded-lg px-2 transition-colors -mx-2">
                 <div className="flex-shrink-0 mt-1">
                   {log.avatar ? (
                     <Avatar src={log.avatar} size={32} className="border border-slate-700" />
                   ) : (
                     <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400">
                       <Bot size={16} />
                     </div>
                   )}
                 </div>
                 <div className="flex-1 min-w-0">
                   <div className="text-sm text-slate-200">
                     <span className="font-semibold text-white">{log.user}</span> {log.action}
                   </div>
                   <div className="text-xs text-slate-500 mt-0.5 font-mono">{log.time}</div>
                 </div>
                 <div className="flex items-center text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity">
                   <GitCommit size={14} />
                 </div>
               </div>
             ))}
          </div>
        </BentoCard>

        {/* Right Column Stack */}
        <div className="flex flex-col gap-6 h-full">
          
          {/* Resource Usage */}
          <BentoCard title="Resource Usage" icon={Cpu} className="flex-1">
             <div className="flex items-center justify-around h-full">
               <div className="relative w-24 h-24 flex items-center justify-center">
                 <ResponsiveContainer width="100%" height="100%">
                   <PieChart>
                     <Pie
                       data={quotaData}
                       innerRadius={35}
                       outerRadius={45}
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
                   <span className="text-lg font-bold text-white">75%</span>
                   <span className="text-[10px] text-slate-400 uppercase">API Quota</span>
                 </div>
               </div>

               <div className="relative w-24 h-24 flex items-center justify-center">
                 <ResponsiveContainer width="100%" height="100%">
                   <PieChart>
                     <Pie
                       data={storageData}
                       innerRadius={35}
                       outerRadius={45}
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
                   <span className="text-lg font-bold text-white">42%</span>
                   <span className="text-[10px] text-slate-400 uppercase">RAG Storage</span>
                 </div>
               </div>
             </div>
          </BentoCard>

          {/* System Health */}
          <BentoCard title="System Health" icon={Server} className="flex-1">
             <div className="space-y-4">
                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950/50 border border-slate-800">
                  <div className="flex items-center gap-3">
                    <Database size={16} className="text-cyan-400" />
                    <span className="text-sm font-medium text-slate-300">RAG Service</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500 font-mono">14ms</span>
                    <StatusDot status="healthy" />
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950/50 border border-slate-800">
                  <div className="flex items-center gap-3">
                    <Zap size={16} className="text-indigo-400" />
                    <span className="text-sm font-medium text-slate-300">Runner Service</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500 font-mono">230ms</span>
                    <StatusDot status="healthy" />
                  </div>
                </div>
             </div>
          </BentoCard>
          
        </div>
      </div>
    </div>
  );
};
