import { type FC, useState } from 'react';
import { Layout, Menu, Button, Avatar, Dropdown, theme } from 'antd';
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
import { motion, AnimatePresence } from 'framer-motion';

const { Header, Sider, Content } = Layout;

export const DashboardLayout: FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { token } = theme.useToken();

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
      label: '质量分析',
      onClick: () => navigate('/dashboard/analytics'),
    },
    {
      key: '/dashboard/team',
      icon: <Users size={18} />,
      label: '团队权限',
      onClick: () => navigate('/dashboard/team'),
    },
    {
      key: '/dashboard/settings',
      icon: <Settings size={18} />,
      label: '环境设置',
      onClick: () => navigate('/dashboard/settings'),
    },
    {
      key: '/dashboard/profile',
      icon: <Bot size={18} />,
      label: '个人资料',
      onClick: () => navigate('/dashboard/profile'),
    },
    {
      key: '/dashboard/integrations',
      icon: <Share2 size={18} />,
      label: '集成',
      onClick: () => navigate('/dashboard/integrations'),
    }
  ];

  return (
    <Layout className="min-h-screen bg-cyber-black selection:bg-neon-cyan/30 selection:text-neon-cyan">
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        size={260}
        className="!bg-slate-950/80 backdrop-blur-xl border-r border-slate-800/50 z-20"
        style={{
            position: 'fixed',
            left: 0,
            top: 0,
            bottom: 0,
            height: '100vh',
            overflowY: 'auto'
        }}
      >
        <div className="h-16 flex items-center justify-center border-b border-slate-800/50">
           <div className={`transition-all duration-300 ${collapsed ? 'scale-75' : 'scale-100'}`}>
             <Logo size={collapsed ? 32 : 120} />
           </div>
        </div>
        
        <div className="py-4 px-2">
            <Menu
              mode="inline"
              selectedKeys={[location.pathname]}
              items={menuItems}
              className="!bg-transparent !border-none"
              theme="dark"
              style={{ background: 'transparent' }}
            />
        </div>
      </Sider>
      
      <Layout className={`transition-all duration-300 ${collapsed ? 'ml-[80px]' : 'ml-[260px]'} bg-transparent`}>
        <Header className="!bg-slate-900/60 !backdrop-blur-md !border-b !border-slate-800/50 !h-16 !px-6 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <Button
              type="text"
              icon={<MenuIcon size={20} className="text-slate-400" />}
              onClick={() => setCollapsed(!collapsed)}
              className="!text-slate-400 hover:!text-neon-cyan hover:!bg-neon-cyan/10"
            />
            
            <div className="hidden md:flex items-center px-4 py-2 bg-slate-800/50 rounded-lg border border-slate-700/50 focus-within:border-neon-cyan/50 focus-within:ring-1 focus-within:ring-neon-cyan/20 transition-all w-64">
                <Search size={16} className="text-slate-500 mr-2" />
                <input 
                    type="text" 
                    placeholder="Search..." 
                    className="bg-transparent border-none outline-none text-sm text-slate-200 w-full placeholder:text-slate-500"
                />
            </div>
          </div>

          <div className="flex items-center gap-4">
             <Button 
                type="text" 
                icon={<Bell size={20} />} 
                className="!text-slate-400 hover:!text-neon-cyan hover:!bg-neon-cyan/10 !flex !items-center !justify-center"
             />
             
             <div className="h-8 w-[1px] bg-slate-800 mx-2" />
             
             <Dropdown 
                menu={{ 
                    items: [
                        { key: 'profile', label: '个人资料', icon: <Bot size={14}/> },
                        { key: 'settings', label: '设置', icon: <Settings size={14}/> },
                        { type: 'divider' },
                        { key: 'logout', label: '登出', icon: <LogOut size={14}/>, danger: true }
                    ] 
                }}
             >
                <div className="flex items-center gap-3 cursor-pointer hover:bg-slate-800/50 p-2 rounded-lg transition-colors">
                    <Avatar 
                        src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" 
                        className="border border-neon-cyan/30"
                    />
                    <div className="hidden md:block text-left">
                        <div className="text-sm font-medium text-slate-200">Admin User</div>
                        <div className="text-xs text-slate-500">Administrator</div>
                    </div>
                    <ChevronDown size={14} className="text-slate-500" />
                </div>
             </Dropdown>
          </div>
        </Header>
        
        <Content className="p-6 min-h-[calc(100vh-64px)] overflow-x-hidden">
          <AnimatePresence mode="wait">
            <motion.div
                key={location.pathname}
                initial={{ opacity: 0, y: 20, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.98 }}
                transition={{ duration: 0.3, ease: "easeOut" }}
                className="h-full"
            >
                <Outlet />
            </motion.div>
          </AnimatePresence>
        </Content>
      </Layout>
    </Layout>
  );
};


