import React from 'react';
import { Form, Input, Button, Checkbox } from 'antd';
import { useNavigate } from 'react-router-dom';
import { User, Lock, Github, Gitlab, ArrowRight, Zap } from 'lucide-react';
import { Logo } from '../components/Logo';
import { motion } from 'framer-motion';

interface LoginValues {
  email: string;
}

export const Login: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  // const { token } = theme.useToken(); // Removed unused token

  const onFinish = (values: LoginValues) => {
    console.log('Success:', values);
    navigate('/workspace');
  };

  return (
    <div className="flex min-h-screen w-full bg-white overflow-hidden">
      {/* Left Side - Visual */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-slate-50 items-center justify-center overflow-hidden border-r border-slate-200">
        <div className="absolute inset-0 z-0 opacity-10 pattern-grid-lg text-primary" />

        <div className="relative z-10 p-12 max-w-lg">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-8"
          >
            <Logo size={48} className="mb-6" />
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl font-bold font-sans tracking-tight mb-6 text-slate-900 leading-tight"
          >
            构建未来。<br />
            <span className="text-primary">
              智能构建。
            </span>
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg text-slate-600 max-w-md leading-relaxed"
          >
            访问专为下一代智能体设计的先进 AI 测试平台。
          </motion.p>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mt-12 flex gap-4"
          >
            <div className="px-4 py-2 border border-slate-200 rounded-full bg-white shadow-sm flex items-center gap-2 text-sm text-slate-600">
              <Zap size={14} className="text-amber-500 fill-amber-500" />
              <span>v2.4.0 实验版</span>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Right Side - Form */}
      <div className="flex-1 flex flex-col items-center justify-center p-4 sm:p-8 lg:p-12 bg-white">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-[400px] space-y-6"
        >
          <div className="text-center lg:text-left space-y-2 mb-8">
            <div className="lg:hidden flex justify-center mb-6">
              <Logo size={40} />
            </div>
            <h2 className="text-3xl font-bold tracking-tight text-slate-900">
              欢迎回来
            </h2>
            <p className="text-slate-500">
              请输入您的凭据以访问工作区
            </p>
          </div>

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
            className="space-y-4"
          >
            <Form.Item
              name="email"
              label="邮箱"
              rules={[
                { required: true, message: '请输入您的邮箱' },
                { type: 'email', message: '请输入有效的邮箱地址' }
              ]}
            >
              <Input
                prefix={<User className="text-slate-400 w-4 h-4" />}
                placeholder="name@company.com"
                className="hover:border-primary focus:border-primary"
              />
            </Form.Item>

            <Form.Item
              name="password"
              label="密码"
              rules={[{ required: true, message: '请输入您的密码' }]}
            >
              <Input.Password
                prefix={<Lock className="text-slate-400 w-4 h-4" />}
                placeholder="••••••••"
                className="hover:border-primary focus:border-primary"
              />
            </Form.Item>

            <div className="flex items-center justify-between">
              <Form.Item name="remember" valuePropName="checked" noStyle>
                <Checkbox className="text-slate-500">记住我</Checkbox>
              </Form.Item>
              <a className="text-sm font-medium text-primary hover:text-blue-700" href="#">
                忘记密码？
              </a>
            </div>

            <Button
              type="primary"
              htmlType="submit"
              block
              className="h-11 bg-primary hover:!bg-blue-700 shadow-sm border-none font-medium text-base rounded-lg mt-2"
            >
              登录
            </Button>
          </Form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-xs uppercase text-slate-400">
              <span className="bg-white px-2">或其他方式登录</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Button
              className="flex items-center justify-center h-10 border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700"
            >
              <Github className="w-4 h-4 mr-2" />
              GitHub
            </Button>
            <Button
              className="flex items-center justify-center h-10 border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700"
            >
              <Gitlab className="w-4 h-4 mr-2 text-orange-600" />
              GitLab
            </Button>
          </div>

          <div className="mt-8 text-center text-sm text-slate-500">
            还没有账号？{' '}
            <a href="#" className="font-semibold text-primary hover:text-blue-700 ml-1 inline-flex items-center">
              注册 <ArrowRight size={14} className="ml-1" />
            </a>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
