import React from 'react';
import { Form, Input, Button, Checkbox } from 'antd';
import { useNavigate } from 'react-router-dom';
import { User, Lock, Eye, EyeOff, Github, Gitlab, Zap } from 'lucide-react';
import { Logo } from '../components/Logo';
import { motion } from 'framer-motion';

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
    <div className="flex h-screen w-full bg-cyber-black text-slate-50 overflow-hidden">
      {/* Left Side - Visual */}
      <div className="hidden lg:flex lg:w-[60%] relative bg-slate-950 items-center justify-center overflow-hidden">
        {/* Background Image with Overlay */}
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1635070041078-e363dbe005cb?q=80&w=2070&auto=format&fit=crop" 
            alt="Cyberpunk Network" 
            className="w-full h-full object-cover opacity-60 scale-105 animate-pulse-slow"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-cyber-black via-slate-900/80 to-transparent" />
          <div className="absolute inset-0 bg-indigo-900/30 mix-blend-overlay" />
          {/* Animated Grid Overlay */}
          <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20" />
        </div>

        {/* Content Overlay */}
        <div className="relative z-10 p-12 max-w-2xl">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="mb-8"
          >
            <Logo size={64} className="scale-110 origin-left mb-6 drop-shadow-[0_0_15px_rgba(0,243,255,0.5)]" />
          </motion.div>
          <motion.h1 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-6xl font-bold font-display tracking-tight mb-6 text-white drop-shadow-2xl leading-tight">
            守护未来。<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-neon-cyan via-white to-neon-purple animate-text-shimmer bg-[length:200%_auto]">
              智能构建。
            </span>
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-xl text-slate-300 max-w-lg leading-relaxed font-light"
          >
            访问专为下一代智能体设计的先进 AI 测试平台。
            <br />
            <span className="text-neon-cyan font-mono text-sm mt-2 block">{">"} 精确监控 // 调试 // 部署</span>
          </motion.p>
          
          {/* Decorative Elements */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.8 }}
            className="mt-16 flex gap-4 text-xs font-mono text-slate-500"
          >
             <div className="px-4 py-1.5 border border-slate-700/50 rounded-full bg-slate-900/50 backdrop-blur-md shadow-lg flex items-center gap-2">
                <Zap size={12} className="text-yellow-400 fill-yellow-400" />
                v2.4.0-beta
             </div>
             <div className="px-4 py-1.5 border border-slate-700/50 rounded-full bg-slate-900/50 backdrop-blur-md shadow-lg flex items-center gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-neon-green animate-ping" />
                <div className="w-1.5 h-1.5 rounded-full bg-neon-green -ml-3.5" />
                SYSTEM ONLINE
             </div>
          </motion.div>
        </div>
      </div>

      {/* Right Side - Form */}
      <div className="flex-1 flex flex-col items-center justify-center p-4 sm:p-8 lg:p-12 relative bg-cyber-black">
        {/* Mobile Background Effect */}
        <div className="absolute inset-0 bg-grid-slate-800/[0.2] bg-position-[bottom_1px_center] lg:hidden pointer-events-none" />
        
        {/* Background Noise */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-5 pointer-events-none" />

        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="w-full max-w-md space-y-8 relative z-10"
        >
          {/* Header */}
          <div className="text-center space-y-2">
            <div className="lg:hidden flex justify-center mb-6">
               <Logo size={40} />
            </div>
            <h2 className="text-4xl font-bold tracking-tight text-white font-display">
              欢迎回来
            </h2>
            <p className="text-sm text-slate-400 font-mono">
              输入您的凭据以访问工作空间
            </p>
          </div>

          {/* Card Container */}
          <div className="p-8 rounded-2xl border border-slate-700/50 bg-slate-900/40 backdrop-blur-xl shadow-[0_0_40px_rgba(0,0,0,0.5)] relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-neon-cyan to-transparent opacity-50" />
            
            <Form
              form={form}
              name="login"
              layout="vertical"
              onFinish={onFinish}
              requiredMark={false}
              size="large"
              initialValues={{
                email: 'admin@nexus.os',
                password: 'password123',
                remember: true
              }}
            >
              <Form.Item
                name="email"
                label={<span className="text-slate-300 font-medium text-xs uppercase tracking-wider">邮箱</span>}
                rules={[
                  { required: true, message: '请输入您的邮箱!' },
                  { type: 'email', message: '请输入有效的邮箱地址!' }
                ]}
              >
                <Input 
                  prefix={<User className="text-slate-500 w-4 h-4" />} 
                  placeholder="name@company.com" 
                  className="bg-slate-950/50! border-slate-700! hover:border-neon-cyan! focus:border-neon-cyan! text-slate-200! placeholder:text-slate-600! h-12! rounded-lg!"
                />
              </Form.Item>

              <Form.Item
                name="password"
                label={<span className="text-slate-300 font-medium text-xs uppercase tracking-wider">密码</span>}
                rules={[{ required: true, message: '请输入您的密码!' }]}
              >
                <Input.Password
                  prefix={<Lock className="text-slate-500 w-4 h-4" />}
                  placeholder="••••••••"
                  iconRender={(visible) => (visible ? <Eye className="text-slate-500 w-4 h-4" /> : <EyeOff className="text-slate-500 w-4 h-4" />)}
                  className="bg-slate-950/50! border-slate-700! hover:border-neon-cyan! focus:border-neon-cyan! text-slate-200! placeholder:text-slate-600! h-12! rounded-lg!"
                />
              </Form.Item>

              <div className="flex items-center justify-between mb-8">
                <Form.Item name="remember" valuePropName="checked" noStyle>
                  <Checkbox className="text-slate-400 hover:text-neon-cyan login-checkbox">记住我</Checkbox>
                </Form.Item>
                <a className="text-xs font-medium text-neon-cyan hover:text-white transition-colors uppercase tracking-wide" href="#">
                  忘记密码?
                </a>
              </div>

              <Form.Item className="mb-4">
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  block
                  className="h-12! bg-neon-cyan! hover:bg-white! text-black! border-0! shadow-[0_0_20px_rgba(0,243,255,0.3)]! hover:shadow-[0_0_30px_rgba(0,243,255,0.5)]! font-bold! tracking-widest! uppercase! transition-all! duration-300! transform! hover:scale-[1.02]!"
                >
                  登录系统
                </Button>
              </Form.Item>
            </Form>

            <div className="relative my-8">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-slate-800" />
              </div>
              <div className="relative flex justify-center text-[10px] uppercase tracking-widest">
                <span className="bg-slate-900/80 px-2 text-slate-500">或继续使用</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Button 
                className="flex! items-center! justify-center! h-10! bg-slate-950/50! border-slate-700! hover:bg-slate-800! hover:border-white! text-slate-300! hover:text-white! transition-all rounded-lg!"
              >
                <Github className="w-4 h-4 mr-2" />
                GitHub
              </Button>
              <Button 
                className="flex! items-center! justify-center! h-10! bg-slate-950/50! border-slate-700! hover:bg-slate-800! hover:border-orange-500! text-slate-300! hover:text-white! transition-all rounded-lg!"
              >
                <Gitlab className="w-4 h-4 mr-2 text-orange-500" />
                GitLab
              </Button>
            </div>

            <div className="mt-8 text-center text-xs text-slate-500">
              还没有账户?{' '}
              <a href="#" className="font-bold text-neon-cyan hover:text-white transition-colors ml-1">
                立即注册 {">"}
              </a>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
