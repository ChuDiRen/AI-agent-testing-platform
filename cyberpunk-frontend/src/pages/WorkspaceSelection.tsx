import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Avatar } from 'antd';
import { Plus, Users, Clock, ArrowRight } from 'lucide-react';
import { Logo } from '../components/Logo';

interface Workspace {
  id: string;
  name: string;
  icon: string;
  members: string[];
  lastActive: string;
  role: 'Owner' | 'Editor' | 'Viewer';
}

const mockWorkspaces: Workspace[] = [
  {
    id: '1',
    name: '新东京项目',
    icon: 'https://images.unsplash.com/photo-1535295972055-1c762f4483e5?w=100&h=100&fit=crop',
    members: [
      'https://i.pravatar.cc/150?u=1',
      'https://i.pravatar.cc/150?u=2',
      'https://i.pravatar.cc/150?u=3',
      'https://i.pravatar.cc/150?u=4'
    ],
    lastActive: '2 分钟前',
    role: 'Owner'
  },
  {
    id: '2',
    name: '网络防御运营',
    icon: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=100&h=100&fit=crop',
    members: [
      'https://i.pravatar.cc/150?u=5',
      'https://i.pravatar.cc/150?u=6'
    ],
    lastActive: '1 小时前',
    role: 'Editor'
  },
  {
    id: '3',
    name: 'AI 神经网络',
    icon: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=100&h=100&fit=crop',
    members: [
      'https://i.pravatar.cc/150?u=7',
      'https://i.pravatar.cc/150?u=8',
      'https://i.pravatar.cc/150?u=9'
    ],
    lastActive: '3 天前',
    role: 'Viewer'
  },
  {
    id: '4',
    name: '量子核心',
    icon: 'https://images.unsplash.com/photo-1614728853913-1e2211eb5d95?w=100&h=100&fit=crop',
    members: [
      'https://i.pravatar.cc/150?u=10'
    ],
    lastActive: '1 周前',
    role: 'Owner'
  },
  {
    id: '5',
    name: 'Nexus 原型',
    icon: 'https://images.unsplash.com/photo-1614726365723-49cfa956c802?w=100&h=100&fit=crop',
    members: [
      'https://i.pravatar.cc/150?u=11',
      'https://i.pravatar.cc/150?u=12'
    ],
    lastActive: '2 weeks ago',
    role: 'Editor'
  }
];

export const WorkspaceSelection: React.FC = () => {
  const navigate = useNavigate();

  const handleWorkspaceClick = (id: string) => {
    console.log(`Entering workspace ${id}`);
    navigate('/dashboard'); 
  };

  return (
    <div className="min-h-screen w-full bg-slate-900 text-slate-50 relative overflow-hidden flex flex-col">
      {/* Background Grid */}
      <div className="absolute inset-0 bg-grid-slate-800/[0.2] pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-b from-slate-900 via-transparent to-slate-900 pointer-events-none" />

      {/* Header */}
      <div className="relative z-10 w-full max-w-7xl mx-auto px-6 py-8 flex justify-between items-center">
        <Logo size={32} />
        <div className="flex items-center gap-4">
          <Avatar src="https://i.pravatar.cc/150?u=me" className="border border-slate-700" />
          <div className="text-sm">
            <div className="font-medium text-slate-200">Alex Chen</div>
            <div className="text-xs text-slate-500">alex@nexus.os</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-center p-6 max-w-6xl mx-auto w-full">
        <div className="text-center mb-12 space-y-4">
          <h1 className="text-3xl md:text-4xl font-bold font-sans tracking-tight text-white">
            Select your workspace
          </h1>
          <p className="text-slate-400 text-lg max-w-xl mx-auto">
            Access your projects, manage agents, and monitor performance across different environments.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full">
          {mockWorkspaces.map((workspace) => (
            <div
              key={workspace.id}
              onClick={() => handleWorkspaceClick(workspace.id)}
              className="group relative p-6 rounded-xl border border-slate-700/50 bg-slate-800/50 backdrop-blur-sm cursor-pointer transition-all duration-300 hover:border-neon-cyan/50 hover:shadow-[0_0_20px_rgba(99,102,241,0.15)] hover:-translate-y-1"
            >
              <div className="flex items-start justify-between mb-4">
                <Avatar 
                  shape="square" 
                  size={48} 
                  src={workspace.icon} 
                  className="rounded-lg border border-slate-600 group-hover:border-neon-cyan/50 transition-colors"
                />
                <div className={`text-xs px-2 py-1 rounded-full border ${
                  workspace.role === 'Owner' 
                    ? 'bg-neon-cyan/10 border-neon-cyan/20 text-neon-cyan' 
                    : 'bg-slate-700/30 border-slate-600/50 text-slate-400'
                }`}>
                  {workspace.role}
                </div>
              </div>

              <h3 className="text-xl font-bold text-slate-100 mb-2 group-hover:text-neon-cyan transition-colors">
                {workspace.name}
              </h3>

              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm text-slate-400">
                  <div className="flex items-center gap-1.5">
                    <Clock size={14} />
                    <span>{workspace.lastActive}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Users size={14} />
                    <span>{workspace.members.length} members</span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-slate-700/50">
                  <Avatar.Group max={{ count: 4 }} size="small" className="!ml-1">
                    {workspace.members.map((member, i) => (
                      <Avatar key={i} src={member} className="border-slate-800" />
                    ))}
                  </Avatar.Group>
                  <ArrowRight className="w-5 h-5 text-slate-600 group-hover:text-neon-cyan transform group-hover:translate-x-1 transition-all" />
                </div>
              </div>
            </div>
          ))}

          {/* Create New Workspace Card */}
          <button className="group flex flex-col items-center justify-center p-6 rounded-xl border-2 border-dashed border-slate-700 bg-slate-800/20 hover:bg-slate-800/40 hover:border-neon-cyan/50 transition-all duration-300 min-h-[220px]">
            <div className="w-16 h-16 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center mb-4 group-hover:border-neon-cyan/50 group-hover:bg-neon-cyan/10 transition-all">
              <Plus className="w-8 h-8 text-slate-400 group-hover:text-neon-cyan" />
            </div>
            <h3 className="text-lg font-semibold text-slate-300 group-hover:text-neon-cyan transition-colors">
              Create New Workspace
            </h3>
            <p className="text-sm text-slate-500 mt-2 text-center max-w-[200px]">
              Set up a new environment for your team
            </p>
          </button>
        </div>
      </div>
    </div>
  );
};

