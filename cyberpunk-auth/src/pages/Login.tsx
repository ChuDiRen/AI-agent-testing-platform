import React from 'react';
import { Form, Input, Button, Checkbox } from 'antd';
import { useNavigate } from 'react-router-dom';
import { User, Lock, Eye, EyeOff, Github, Gitlab } from 'lucide-react';
import { Logo } from '../components/Logo';

interface LoginValues {
  email: string;
}

export const Login: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const onFinish = (values: LoginValues) => {
    console.log('Success:', values);
    navigate('/workspace');
  };

  return (
    <div className="flex h-screen w-full bg-slate-900 text-slate-50 overflow-hidden">
      {/* Left Side - Visual */}
      <div className="hidden lg:flex lg:w-[60%] relative bg-slate-950 items-center justify-center overflow-hidden">
        {/* Background Image with Overlay */}
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1635070041078-e363dbe005cb?q=80&w=2070&auto=format&fit=crop" 
            alt="Cyberpunk Network" 
            className="w-full h-full object-cover opacity-80"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/60 to-transparent" />
          <div className="absolute inset-0 bg-indigo-900/20 mix-blend-overlay" />
        </div>

        {/* Content Overlay */}
        <div className="relative z-10 p-12 max-w-2xl">
          <div className="mb-8">
            <Logo size={48} className="scale-125 origin-left mb-6" />
          </div>
          <h1 className="text-5xl font-bold font-sans tracking-tight mb-6 text-white drop-shadow-lg">
            守护未来。<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">
              智能构建。
            </span>
          </h1>
          <p className="text-lg text-slate-300 max-w-lg leading-relaxed">
            访问专为下一代智能体设计的先进 AI 测试平台。
            精确监控、调试和部署。
          </p>
          
          {/* Decorative Elements */}
          <div className="mt-12 flex gap-4 text-xs font-mono text-slate-500">
             <div className="px-3 py-1 border border-slate-700 rounded-full bg-slate-900/50 backdrop-blur-sm">
                v2.4.0-beta
             </div>
             <div className="px-3 py-1 border border-slate-700 rounded-full bg-slate-900/50 backdrop-blur-sm flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                SYSTEM ONLINE
             </div>
          </div>
        </div>
      </div>

      {/* Right Side - Form */}
      <div className="flex-1 flex flex-col items-center justify-center p-4 sm:p-8 lg:p-12 relative bg-slate-900">
        {/* Mobile Background Effect */}
        <div className="absolute inset-0 bg-grid-slate-800/[0.2] bg-[bottom_1px_center] lg:hidden pointer-events-none" />

        <div className="w-full max-w-md space-y-8 relative z-10">
          {/* Header */}
          <div className="text-center space-y-2">
            <div className="lg:hidden flex justify-center mb-4">
               <Logo />
            </div>
            <h2 className="text-3xl font-bold tracking-tight text-white font-sans">
              欢迎回来
            </h2>
            <p className="text-sm text-slate-400">
              输入您的凭据以访问工作空间
            </p>
          </div>

          {/* Card Container */}
          <div className="p-8 rounded-xl border border-slate-700/50 bg-slate-800/50 backdrop-blur-xl shadow-2xl ring-1 ring-white/5">
            <Form
              form={form}
              name="login"
              layout="vertical"
              onFinish={onFinish}
              requiredMark={false}
              size="large"
            >
              <Form.Item
                name="email"
                label={<span className="text-slate-300 font-medium">邮箱</span>}
                rules={[
                  { required: true, message: '请输入您的邮箱!' },
                  { type: 'email', message: '请输入有效的邮箱地址!' }
                ]}
              >
                <Input 
                  prefix={<User className="text-slate-500 w-4 h-4" />} 
                  placeholder="name@company.com" 
                  className="!bg-slate-900/50 !border-slate-700 hover:!border-indigo-500 focus:!border-indigo-500 !text-slate-200 placeholder:!text-slate-600"
                />
              </Form.Item>

              <Form.Item
                name="password"
                label={<span className="text-slate-300 font-medium">密码</span>}
                rules={[{ required: true, message: '请输入您的密码!' }]}
              >
                <Input.Password
                  prefix={<Lock className="text-slate-500 w-4 h-4" />}
                  placeholder="••••••••"
                  iconRender={(visible) => (visible ? <Eye className="text-slate-500 w-4 h-4" /> : <EyeOff className="text-slate-500 w-4 h-4" />)}
                  className="!bg-slate-900/50 !border-slate-700 hover:!border-indigo-500 focus:!border-indigo-500 !text-slate-200 placeholder:!text-slate-600"
                />
              </Form.Item>

              <div className="flex items-center justify-between mb-6">
                <Form.Item name="remember" valuePropName="checked" noStyle>
                  <Checkbox className="text-slate-400 hover:text-indigo-400">记住我</Checkbox>
                </Form.Item>
                <a className="text-sm font-medium text-indigo-400 hover:text-indigo-300 transition-colors" href="#">
                  忘记密码?
                </a>
              </div>

              <Form.Item className="mb-4">
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  block
                  className="!h-11 !bg-gradient-to-r !from-indigo-600 !to-cyan-600 hover:!from-indigo-500 hover:!to-cyan-500 !border-0 !shadow-[0_0_20px_rgba(99,102,241,0.3)] !text-white !font-semibold !tracking-wide"
                >
                  登录
                </Button>
              </Form.Item>
            </Form>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-slate-700" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-slate-800 px-2 text-slate-500">或继续使用</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Button 
                className="!flex !items-center !justify-center !h-10 !bg-slate-900/50 !border-slate-700 hover:!bg-slate-800 hover:!border-indigo-500/50 !text-slate-300 transition-all"
              >
                <Github className="w-4 h-4 mr-2" />
                GitHub
              </Button>
              <Button 
                className="!flex !items-center !justify-center !h-10 !bg-slate-900/50 !border-slate-700 hover:!bg-slate-800 hover:!border-indigo-500/50 !text-slate-300 transition-all"
              >
                <Gitlab className="w-4 h-4 mr-2 text-orange-500" />
                GitLab
              </Button>
            </div>

            <div className="mt-6 text-center text-sm text-slate-400">
              还没有账户?{' '}
              <a href="#" className="font-medium text-indigo-400 hover:text-indigo-300 hover:underline underline-offset-4">
                创建账户
              </a>
            </div>
          </div>
          
          <p className="text-center text-xs text-slate-600 mt-8">
            &copy; 2026 NEXUS.OS Inc. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  );
};
