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
  role: '所有者' | '编辑者' | '访客';
}

const mockWorkspaces: Workspace[] = [
  {
    id: '1',
    name: 'New Tokyo Project',
    icon: 'https://images.unsplash.com/photo-1535295972055-1c762f4483e5?w=100&h=100&fit=crop',
    members: [
      'https://i.pravatar.cc/150?u=1',
      'https://i.pravatar.cc/150?u=2',
      'https://i.pravatar.cc/150?u=3',
      'https://i.pravatar.cc/150?u=4'
    ],
    lastActive: '2 分钟前',
    role: '所有者'
  },
  {
    id: '2',
    name: 'Cyber Defense Ops',
    icon: 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=100&h=100&fit=crop',
    members: [
      'https://i.pravatar.cc/150?u=5',
      'https://i.pravatar.cc/150?u=6'
    ],
    lastActive: '1 小时前',
    role: '编辑者'
  },
  {
    id: '3',
    name: 'AI Neural Net',
    icon: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=100&h=100&fit=crop',
    members: [
      'https://i.pravatar.cc/150?u=7',
      'https://i.pravatar.cc/150?u=8',
      'https://i.pravatar.cc/150?u=9'
    ],
    lastActive: '3 天前',
    role: '访客'
  },
  {
    id: '4',
    name: 'Quantum Core',
    icon: 'https://images.unsplash.com/photo-1614728853913-1e2211eb5d95?w=100&h=100&fit=crop',
    members: [
      'https://i.pravatar.cc/150?u=10'
    ],
    lastActive: '1 周前',
    role: '所有者'
  },
  {
    id: '5',
    name: 'Nexus Prototype',
    icon: 'https://images.unsplash.com/photo-1614726365723-49cfa956c802?w=100&h=100&fit=crop',
    members: [
      'https://i.pravatar.cc/150?u=11',
      'https://i.pravatar.cc/150?u=12'
    ],
    lastActive: '2 周前',
    role: '编辑者'
  }
];

export const WorkspaceSelection: React.FC = () => {
  const navigate = useNavigate();

  const handleWorkspaceClick = (id: string) => {
    console.log(`Entering workspace ${id}`);
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen w-full bg-slate-50 relative overflow-hidden flex flex-col">
      {/* Header */}
      <div className="relative z-10 w-full max-w-7xl mx-auto px-6 py-6 flex justify-between items-center bg-white/50 backdrop-blur-sm sticky top-0 border-b border-slate-200">
        <Logo size={28} />
        <div className="flex items-center gap-4">
          <Avatar src="https://i.pravatar.cc/150?u=me" className="border border-slate-200" />
          <div className="text-sm">
            <div className="font-medium text-slate-900">Alex Chen</div>
            <div className="text-xs text-slate-500">alex@nexus.os</div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex flex-col items-center justify-start pt-16 p-6 max-w-6xl mx-auto w-full">
        <div className="text-center mb-12 space-y-3">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            选择您的工作区
          </h1>
          <p className="text-slate-500 text-lg max-w-xl mx-auto">
            访问您的项目，管理智能体，并监控不同环境下的性能。
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full">
          {mockWorkspaces.map((workspace) => (
            <div
              key={workspace.id}
              onClick={() => handleWorkspaceClick(workspace.id)}
              className="group relative p-6 rounded-xl border border-slate-200 bg-white cursor-pointer transition-all duration-200 hover:shadow-lg hover:border-blue-200 hover:-translate-y-0.5"
            >
              <div className="flex items-start justify-between mb-4">
                <Avatar
                  shape="square"
                  size={48}
                  src={workspace.icon}
                  className="rounded-lg border border-slate-100 group-hover:border-blue-100 transition-colors"
                />
                <div className={`text-xs px-2.5 py-0.5 rounded-full border font-medium ${workspace.role === '所有者'
                  ? 'bg-blue-50 border-blue-100 text-blue-700'
                  : 'bg-slate-50 border-slate-100 text-slate-600'
                  }`}>
                  {workspace.role}
                </div>
              </div>

              <h3 className="text-lg font-bold text-slate-900 mb-2 group-hover:text-primary transition-colors">
                {workspace.name}
              </h3>

              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm text-slate-500">
                  <div className="flex items-center gap-1.5">
                    <Clock size={14} />
                    <span>{workspace.lastActive}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Users size={14} />
                    <span>{workspace.members.length} 位成员</span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-slate-50">
                  <Avatar.Group max={{ count: 4 }} size="small" className="!ml-1">
                    {workspace.members.map((member, i) => (
                      <Avatar key={i} src={member} className="border-white" />
                    ))}
                  </Avatar.Group>
                  <ArrowRight className="w-5 h-5 text-slate-300 group-hover:text-primary transform group-hover:translate-x-1 transition-all" />
                </div>
              </div>
            </div>
          ))}

          {/* Create New Workspace Card */}
          <button className="group flex flex-col items-center justify-center p-6 rounded-xl border-2 border-dashed border-slate-200 bg-slate-50/50 hover:bg-white hover:border-blue-400/50 transition-all duration-200 min-h-[220px]">
            <div className="w-14 h-14 rounded-full bg-white border border-slate-200 flex items-center justify-center mb-4 group-hover:border-blue-200 group-hover:shadow-sm transition-all">
              <Plus className="w-6 h-6 text-slate-400 group-hover:text-primary" />
            </div>
            <h3 className="text-base font-semibold text-slate-600 group-hover:text-primary transition-colors">
              创建新工作区
            </h3>
            <p className="text-sm text-slate-400 mt-1 text-center max-w-[200px]">
              为您的团队设置新环境
            </p>
          </button>
        </div>
      </div>
    </div>
  );
};
