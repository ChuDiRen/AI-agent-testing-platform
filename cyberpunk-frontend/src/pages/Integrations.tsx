import React, { useState } from 'react';
import { Card, Switch, Button, Input, Modal, Typography, Tag, Form } from 'antd';
import { motion } from 'framer-motion';
import { CyberCard } from '../components/CyberCard';
import { 
  GitBranch, 
  Github, 
  Gitlab, 
  Slack, 
  Mail, 
  Server, 
  Settings, 
  CheckCircle, 
  XCircle, 
  MessageSquare,
  Link as LinkIcon
} from 'lucide-react';

const { Title, Text, Paragraph } = Typography;

interface Integration {
  id: string;
  name: string;
  type: 'ci-cd' | 'notification' | 'mcp';
  icon: React.ReactNode;
  status: 'active' | 'inactive' | 'connected' | 'disconnected';
  description: string;
  config?: Record<string, unknown>;
}

const Integrations: React.FC = () => {
  const [integrations, setIntegrations] = useState<Integration[]>([
    { id: 'jenkins', name: 'Jenkins', type: 'ci-cd', icon: <GitBranch className="text-orange-400" />, status: 'active', description: '触发构建并从 Jenkins 流水线获取构建产物。' },
    { id: 'github', name: 'GitHub Actions', type: 'ci-cd', icon: <Github className="text-white" />, status: 'inactive', description: '同步工作流运行和状态检查。' },
    { id: 'gitlab', name: 'GitLab CI', type: 'ci-cd', icon: <Gitlab className="text-orange-600" />, status: 'inactive', description: '与 GitLab CI/CD 流水线集成。' },
    { id: 'slack', name: 'Slack', type: 'notification', icon: <Slack className="text-purple-400" />, status: 'active', description: '向 Slack 频道发送测试结果和警报。' },
    { id: 'dingtalk', name: '钉钉', type: 'notification', icon: <MessageSquare className="text-blue-400" />, status: 'inactive', description: '通过钉钉机器人消息通知团队。' },
    { id: 'email', name: '邮件', type: 'notification', icon: <Mail className="text-yellow-400" />, status: 'active', description: '向邮件列表发送摘要报告。' },
    { id: 'mcp-rag', name: 'RAG 服务', type: 'mcp', icon: <Server className="text-neon-purple" />, status: 'connected', description: '用于 RAG 操作的模型上下文协议服务器。', config: { endpoint: 'http://localhost:8080/mcp' } },
    { id: 'mcp-chart', name: '图表服务', type: 'mcp', icon: <Server className="text-pink-400" />, status: 'disconnected', description: '用于生成图表和分析的 MCP 服务器。', config: { endpoint: 'http://localhost:8081/mcp' } },
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentConfig, setCurrentConfig] = useState<Integration | null>(null);
  const [form] = Form.useForm();

  const handleToggle = (id: string, checked: boolean) => {
    setIntegrations(prev => prev.map(item => 
      item.id === id ? { ...item, status: checked ? 'active' : 'inactive' } : item
    ));
  };

  const openConfig = (item: Integration) => {
    setCurrentConfig(item);
    form.setFieldsValue(item.config || {});
    setIsModalOpen(true);
  };

  const handleSaveConfig = () => {
    form.validateFields().then(values => {
      setIntegrations(prev => prev.map(item => 
        item.id === currentConfig?.id ? { ...item, config: { ...item.config, ...values } } : item
      ));
      setIsModalOpen(false);
    });
  };

  const renderStatus = (status: string) => {
    switch(status) {
      case 'active': return <Tag color="success">活跃</Tag>;
      case 'inactive': return <Tag color="default">非活跃</Tag>;
      case 'connected': return <Tag color="success" icon={<CheckCircle size={12} />}>已连接</Tag>;
      case 'disconnected': return <Tag color="error" icon={<XCircle size={12} />}>未连接</Tag>;
      default: return null;
    }
  };

  const renderSection = (title: string, type: Integration['type'], delayOffset: number) => (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delayOffset }}
      className="mb-8"
    >
      <Title level={4} className="!text-slate-300 !mb-4 flex items-center gap-2 font-display tracking-wide">
        <LinkIcon size={20} className="text-neon-cyan" />
        {title}
      </Title>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {integrations.filter(i => i.type === type).map((item, index) => (
          <CyberCard 
            key={item.id}
            delay={delayOffset + 0.1 + (index * 0.05)}
            className={`
              h-full flex flex-col
              ${item.status === 'active' || item.status === 'connected' 
                ? 'border-l-2 border-l-neon-green shadow-[inset_2px_0_0_0_#0aff0a]' 
                : 'border-l-2 border-l-transparent'}
            `}
            hoverEffect={true}
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center border border-slate-700 shadow-inner group-hover:border-neon-cyan/50 transition-colors">
                  {item.icon}
                </div>
                <div>
                  <div className="text-white font-medium text-base font-display">{item.name}</div>
                  {renderStatus(item.status)}
                </div>
              </div>
              
              {type === 'ci-cd' && (
                <Switch 
                  checked={item.status === 'active'} 
                  onChange={(checked) => handleToggle(item.id, checked)}
                  className="bg-slate-700 hover:bg-slate-600"
                />
              )}
              
              {type === 'notification' && (
                 <Button 
                   size="small" 
                   icon={<Settings size={14} />} 
                   className="text-slate-400 hover:text-neon-cyan border-slate-700 hover:border-neon-cyan bg-transparent rounded-sm"
                   onClick={() => openConfig(item)}
                 >
                   Config
                 </Button>
              )}
            </div>

            <Paragraph className="text-slate-400 text-sm h-10 mb-4 line-clamp-2 font-mono text-xs leading-relaxed">
              {item.description}
            </Paragraph>

            {type === 'mcp' && (
              <div className="mt-auto pt-4 border-t border-slate-800/50">
                 <div className="flex gap-2">
                    <Input 
                      size="small" 
                      placeholder="Endpoint URL" 
                      defaultValue={item.config?.endpoint as string | undefined} 
                      className="bg-slate-950 border-slate-800 text-slate-300 text-xs font-mono focus:border-neon-cyan"
                      prefix={<Server size={12} className="text-slate-500" />}
                    />
                    <Button 
                      size="small" 
                      type={item.status === 'connected' ? 'default' : 'primary'}
                      className={
                        item.status === 'connected' 
                          ? 'text-neon-green border-neon-green/30 bg-neon-green/10 font-mono text-xs' 
                          : 'bg-neon-cyan text-black border-none font-bold font-mono text-xs hover:bg-neon-cyan/80'
                      }
                    >
                       {item.status === 'connected' ? 'Check' : 'Connect'}
                    </Button>
                 </div>
              </div>
            )}
          </CyberCard>
        ))}
      </div>
    </motion.div>
  );

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="mb-6"
      >
        <Title level={2} className="!text-white !mb-1 flex items-center gap-3 font-display drop-shadow-md">
          <LinkIcon className="text-neon-purple" />
          Integrations
        </Title>
        <Text className="text-slate-400 font-mono text-sm">Manage connections to external tools, notification channels, and MCP servers.</Text>
      </motion.div>

      {renderSection('CI/CD Pipelines', 'ci-cd', 0.2)}
      {renderSection('Notification Channels', 'notification', 0.3)}
      {renderSection('MCP Servers', 'mcp', 0.4)}

      <Modal
        title={<span className="text-neon-cyan font-display tracking-wide">Configure {currentConfig?.name}</span>}
        open={isModalOpen}
        onOk={handleSaveConfig}
        onCancel={() => setIsModalOpen(false)}
        okText="Save Configuration"
        className="cyberpunk-modal"
        styles={{
          content: { background: 'rgba(5, 5, 5, 0.95)', backdropFilter: 'blur(20px)', border: '1px solid #334155' },
          header: { background: 'transparent', borderBottom: '1px solid #1e293b' }
        }}
        closeIcon={<XCircle className="text-slate-500 hover:text-neon-cyan" />}
      >
        <Form form={form} layout="vertical" className="mt-4">
          {currentConfig?.id === 'slack' && (
             <>
               <Form.Item name="webhookUrl" label={<span className="text-slate-400 font-mono text-xs">Webhook URL</span>} rules={[{ required: true }]}>
                 <Input.Password placeholder="https://hooks.slack.com/services/..." className="bg-slate-950 border-slate-700 text-slate-200" />
               </Form.Item>
               <Form.Item name="channel" label={<span className="text-slate-400 font-mono text-xs">Default Channel</span>}>
                 <Input placeholder="#alerts" className="bg-slate-950 border-slate-700 text-slate-200" />
               </Form.Item>
             </>
          )}
          {currentConfig?.id === 'email' && (
             <Form.Item name="recipients" label={<span className="text-slate-400 font-mono text-xs">Recipients</span>} rules={[{ required: true }]}>
               <Input.TextArea rows={3} placeholder="team@example.com, manager@example.com" className="bg-slate-950 border-slate-700 text-slate-200" />
             </Form.Item>
          )}
          {currentConfig?.id === 'dingtalk' && (
             <Form.Item name="accessToken" label={<span className="text-slate-400 font-mono text-xs">Access Token</span>} rules={[{ required: true }]}>
               <Input.Password placeholder="Enter robot access token" className="bg-slate-950 border-slate-700 text-slate-200" />
             </Form.Item>
          )}
        </Form>
      </Modal>
    </motion.div>
  );
};

export default Integrations;

