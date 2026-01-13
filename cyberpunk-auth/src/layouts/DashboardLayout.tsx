import { type FC, useState } from 'react';
import { Layout, Menu, Button, Avatar, Dropdown } from 'antd';
import { 
  LayoutDashboard, 
  FileText, 
  Settings, 
  Database, 
  Bot, 
  Bell, 
  Search,
  LogOut,
  ChevronDown,
  Menu as MenuIcon,
  BookTemplate,
  Server,
  TestTube,
  Share2,
  ScanText,
  Layers,
  Clock,
  Activity,
  Users
} from 'lucide-react';
import { Logo } from '../components/Logo';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';

const { Header, Sider, Content } = Layout;

export const DashboardLayout: FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  // const { token } = theme.useToken();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <LayoutDashboard size={18} />,
      label: '概览',
      onClick: () => navigate('/dashboard'),
    },
    {
      key: '/dashboard/agents',
      icon: <Bot size={18} />,
      label: '智能体',
      onClick: () => navigate('/dashboard/agents'),
    },
    {
      key: '/dashboard/prompts',
      icon: <BookTemplate size={18} />,
      label: '提示词库',
      onClick: () => navigate('/dashboard/prompts'),
    },
    {
      key: '/dashboard/knowledge',
      icon: <Database size={18} />,
      label: '知识库',
      onClick: () => navigate('/dashboard/knowledge'),
    },
    {
      key: '/dashboard/graph-explorer',
      icon: <Share2 size={18} />,
      label: '图谱浏览器',
      onClick: () => navigate('/dashboard/graph-explorer'),
    },
    {
      key: '/dashboard/chunk-debugger',
      icon: <ScanText size={18} />,
      label: '块调试器',
      onClick: () => navigate('/dashboard/chunk-debugger'),
    },
    {
      key: '/dashboard/api-repository',
      icon: <Server size={18} />,
      label: 'API 仓库',
      onClick: () => navigate('/dashboard/api-repository'),
    },
    {
      key: '/dashboard/test-cases',
      icon: <TestTube size={18} />,
      label: '测试用例',
      onClick: () => navigate('/dashboard/test-cases'),
    },
    {
      key: '/dashboard/test-suites',
      icon: <Layers size={18} />,
      label: '测试套件',
      onClick: () => navigate('/dashboard/test-suites'),
    },
    {
      key: '/dashboard/jobs',
      icon: <Clock size={18} />,
      label: '任务队列',
      onClick: () => navigate('/dashboard/jobs'),
    },
    {
      key: '/dashboard/report-detail',
      icon: <FileText size={18} />,
      label: '报告',
      onClick: () => navigate('/dashboard/report-detail'),
    },
    {
      key: '/dashboard/analytics',
      icon: <Activity size={18} />,
      label: '分析',
      onClick: () => navigate('/dashboard/analytics'),
    },
    {
      key: '/dashboard/team',
      icon: <Users size={18} />,
      label: '团队和角色',
      onClick: () => navigate('/dashboard/team'),
    },
    {
      key: '/dashboard/settings',
      icon: <Settings size={18} />,
      label: '设置',
    },
  ];

  const userMenu = {
    items: [
      {
        key: 'profile',
        label: '个人资料',
        onClick: () => navigate('/dashboard/profile'),
      },
      {
        key: 'logout',
        label: '退出登录',
        icon: <LogOut size={14} />,
        danger: true,
        onClick: () => navigate('/login'),
      },
    ],
  };

  return (
    <Layout className="min-h-screen bg-slate-950">
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        width={260}
        className="!bg-slate-900 border-r border-slate-800"
        style={{
          position: 'fixed',
          height: '100vh',
          left: 0,
          zIndex: 50,
        }}
      >
        <div className="h-16 flex items-center justify-center border-b border-slate-800">
          <div className={`transition-all duration-300 ${collapsed ? 'scale-0 opacity-0 w-0' : 'scale-100 opacity-100'}`}>
            <Logo size={24} />
          </div>
          {collapsed && (
             <div className="w-8 h-8 rounded-full bg-indigo-500/10 flex items-center justify-center text-indigo-500">
               <Bot size={20} />
             </div>
          )}
        </div>
        
        <div className="p-4">
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            className="!bg-transparent border-none"
            style={{ fontSize: '14px' }}
          />
        </div>

        {/* User Profile at Bottom of Sider */}
        <div className="absolute bottom-0 w-full p-4 border-t border-slate-800 bg-slate-900/50 backdrop-blur-sm">
          <Dropdown menu={userMenu} placement="topRight" trigger={['click']}>
            <div className={`flex items-center gap-3 cursor-pointer p-2 rounded-lg hover:bg-slate-800 transition-colors ${collapsed ? 'justify-center' : ''}`}>
              <Avatar src="https://i.pravatar.cc/150?u=me" size={32} className="border border-slate-700" />
              {!collapsed && (
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-slate-200 truncate">Alex Chen</div>
                  <div className="text-xs text-slate-500 truncate">Workspace Admin</div>
                </div>
              )}
              {!collapsed && <ChevronDown size={14} className="text-slate-500" />}
            </div>
          </Dropdown>
        </div>
      </Sider>

      <Layout className={`transition-all duration-300 ${collapsed ? 'ml-[80px]' : 'ml-[260px]'}`}>
        <Header className="!bg-slate-900/80 !backdrop-blur-md !px-6 border-b border-slate-800 sticky top-0 z-40 flex items-center justify-between h-16">
          <div className="flex items-center gap-4">
            <Button 
              type="text" 
              icon={<MenuIcon size={18} className="text-slate-400" />} 
              onClick={() => setCollapsed(!collapsed)}
              className="!text-slate-400 hover:!text-white hover:!bg-slate-800"
            />
            <div className="hidden md:flex items-center gap-2 text-sm text-slate-400">
              <span className="text-slate-500">工作空间</span>
              <span className="text-slate-600">/</span>
              <span className="text-slate-200 font-medium">Neo-Tokyo 项目</span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="relative hidden sm:block">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={16} />
              <input 
                type="text" 
                placeholder="搜索资源..." 
                className="bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-1.5 text-sm text-slate-300 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all w-64"
              />
            </div>
            <Button 
              type="text" 
              icon={<Bell size={18} />} 
              className="!text-slate-400 hover:!text-white hover:!bg-slate-800 !flex !items-center !justify-center"
            />
          </div>
        </Header>

        <Content className="p-6 overflow-y-auto bg-slate-950 min-h-[calc(100vh-64px)]">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};
