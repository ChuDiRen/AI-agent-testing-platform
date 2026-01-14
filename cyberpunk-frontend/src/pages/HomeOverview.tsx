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
import { motion } from 'framer-motion';
import { CyberCard } from '../components/CyberCard';

// --- Mock Data ---

const activityLog = [
  { id: 1, user: 'Alex Chen', action: 'updated swagger.json', time: '10m ago', avatar: 'https://i.pravatar.cc/150?u=me' },
  { id: 2, user: 'Sarah Connor', action: 'fixed Test #102', time: '45m ago', avatar: 'https://i.pravatar.cc/150?u=5' },
  { id: 3, user: 'System', action: 'deployed v2.4.1', time: '2h ago', avatar: null },
  { id: 4, user: 'Mike Ross', action: 'created new agent', time: '5h ago', avatar: 'https://i.pravatar.cc/150?u=7' },
];

const quotaData = [
  { name: 'Used', value: 75, color: '#00f3ff' }, // Neon Cyan
  { name: 'Remaining', value: 25, color: '#1e1e1e' }, // Cyber Light
];

const storageData = [
  { name: 'Used', value: 42, color: '#bc13fe' }, // Neon Purple
  { name: 'Free', value: 58, color: '#1e1e1e' }, // Cyber Light
];

// --- Components ---

const StatusDot = ({ status }: { status: 'healthy' | 'warning' | 'error' }) => {
  const colors = {
    healthy: 'bg-neon-green',
    warning: 'bg-neon-yellow',
    error: 'bg-neon-pink'
  };
  
  return (
    <div className="relative flex items-center justify-center w-3 h-3">
      <span className={`absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping ${colors[status]}`} />
      <span className={`relative inline-flex rounded-full h-2 w-2 ${colors[status]} shadow-[0_0_8px_currentColor]`} />
    </div>
  );
};

export const HomeOverview: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Welcome Banner */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="relative rounded-2xl overflow-hidden border border-slate-800 bg-slate-900 shadow-[0_0_30px_rgba(0,243,255,0.05)] group"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-neon-purple/20 to-neon-cyan/20 opacity-50" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20" />
        <div className="absolute inset-0 animate-scanline bg-[linear-gradient(to_bottom,transparent_50%,rgba(0,243,255,0.02)_50%)] bg-[length:100%_4px]" />
        
        <div className="relative p-8 flex flex-col md:flex-row md:items-center justify-between gap-6 z-10">
          <div>
            <motion.h1 
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="text-4xl font-bold text-white mb-2 font-display tracking-wide cyber-text-glow"
            >
              早上好，Alex。
            </motion.h1>
            <motion.div 
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="flex items-center gap-3 text-slate-300"
            >
              <StatusDot status="healthy" />
              <span className="font-mono text-sm tracking-wider">SYSTEM ONLINE // v2.4.1</span>
            </motion.div>
          </div>
          
          <div className="flex flex-wrap gap-3">
            <Button 
              type="primary" 
              icon={<Plus size={16} />}
              className="cyber-button !h-10 !px-6 !border-none"
            >
              新建测试
            </Button>
            <Button 
              className="!bg-slate-800/50 !backdrop-blur-md !border-slate-700 !text-slate-200 !h-10 hover:!border-neon-cyan hover:!text-neon-cyan transition-all"
              icon={<FileText size={16} />}
            >
              查看报告
            </Button>
            <Button 
              className="!bg-slate-800/50 !backdrop-blur-md !border-slate-700 !text-slate-200 !h-10 hover:!border-neon-cyan hover:!text-neon-cyan transition-all"
              icon={<Settings size={16} />}
            >
              配置 API
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Bento Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-auto md:h-100">
        
        {/* Recent Activity - Takes up 2 columns */}
        <CyberCard 
          title="最近活动" 
          icon={Activity} 
          className="md:col-span-2"
          delay={0.1}
          extra={<Button type="link" size="small" className="!text-neon-cyan hover:!text-white">查看全部</Button>}
        >
          <div className="space-y-0 relative h-full overflow-y-auto pr-2 custom-scrollbar">
             {/* Timeline Line */}
             <div className="absolute left-4.75 top-2 bottom-4 w-[1px] bg-gradient-to-b from-slate-700 via-slate-800 to-transparent z-0" />
             
             {activityLog.map((log, index) => (
               <motion.div 
                 initial={{ opacity: 0, x: -10 }}
                 animate={{ opacity: 1, x: 0 }}
                 transition={{ delay: 0.2 + (index * 0.1) }}
                 key={log.id} 
                 className="relative z-10 flex gap-4 py-3 group hover:bg-white/5 rounded-lg px-2 transition-colors -mx-2 cursor-pointer"
               >
                 <div className="flex-shrink-0 mt-1">
                   {log.avatar ? (
                     <Avatar src={log.avatar} size={32} className="border border-slate-700 ring-2 ring-transparent group-hover:ring-neon-cyan/50 transition-all" />
                   ) : (
                     <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 group-hover:text-neon-cyan group-hover:border-neon-cyan transition-colors">
                       <Bot size={16} />
                     </div>
                   )}
                 </div>
                 <div className="flex-1 min-w-0">
                   <div className="text-sm text-slate-300 group-hover:text-white transition-colors">
                     <span className="font-semibold text-neon-cyan">{log.user}</span> {log.action}
                   </div>
                   <div className="text-xs text-slate-500 mt-0.5 font-mono flex items-center gap-2">
                      {log.time}
                      <span className="w-1 h-1 rounded-full bg-slate-600 group-hover:bg-neon-cyan transition-colors" />
                      <span className="opacity-0 group-hover:opacity-100 transition-opacity text-neon-cyan">#{log.id}</span>
                   </div>
                 </div>
                 <div className="flex items-center text-slate-600 opacity-0 group-hover:opacity-100 transition-all transform translate-x-2 group-hover:translate-x-0">
                   <GitCommit size={14} className="text-neon-cyan" />
                 </div>
               </motion.div>
             ))}
          </div>
        </CyberCard>

        {/* Right Column Stack */}
        <div className="flex flex-col gap-6 h-full">
          
          {/* Resource Usage */}
          <CyberCard title="资源监控" icon={Cpu} className="flex-1" delay={0.2}>
             <div className="flex items-center justify-around h-full">
               <div className="relative w-24 h-24 flex items-center justify-center group">
                 <div className="absolute inset-0 rounded-full border border-slate-800 group-hover:border-neon-cyan/30 transition-colors" />
                 <ResponsiveContainer width={96} height={96}>
                   <PieChart>
                     <Pie
                       data={quotaData}
                       innerRadius={38}
                       outerRadius={42}
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
                   <span className="text-xl font-bold text-white font-mono cyber-text-glow">75%</span>
                   <span className="text-[10px] text-slate-400 uppercase tracking-widest">API</span>
                 </div>
               </div>

               <div className="relative w-24 h-24 flex items-center justify-center group">
                 <div className="absolute inset-0 rounded-full border border-slate-800 group-hover:border-neon-purple/30 transition-colors" />
                 <ResponsiveContainer width={96} height={96}>
                   <PieChart>
                     <Pie
                       data={storageData}
                       innerRadius={38}
                       outerRadius={42}
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
                   <span className="text-xl font-bold text-white font-mono" style={{ textShadow: '0 0 10px rgba(188, 19, 254, 0.5)' }}>42%</span>
                   <span className="text-[10px] text-slate-400 uppercase tracking-widest">RAG</span>
                 </div>
               </div>
             </div>
          </CyberCard>

          {/* System Health */}
          <CyberCard title="系统状态" icon={Server} className="flex-1" delay={0.3}>
             <div className="space-y-4">
                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950/50 border border-slate-800 hover:border-neon-cyan/30 transition-colors group">
                  <div className="flex items-center gap-3">
                    <Database size={16} className="text-neon-cyan group-hover:animate-pulse" />
                    <span className="text-sm font-medium text-slate-300">RAG Service</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500 font-mono group-hover:text-neon-cyan transition-colors">14ms</span>
                    <StatusDot status="healthy" />
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 rounded-lg bg-slate-950/50 border border-slate-800 hover:border-neon-purple/30 transition-colors group">
                  <div className="flex items-center gap-3">
                    <Zap size={16} className="text-neon-purple group-hover:animate-pulse" />
                    <span className="text-sm font-medium text-slate-300">Runner Service</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-500 font-mono group-hover:text-neon-purple transition-colors">230ms</span>
                    <StatusDot status="healthy" />
                  </div>
                </div>
             </div>
          </CyberCard>
          
        </div>
      </div>
    </div>
  );
};


