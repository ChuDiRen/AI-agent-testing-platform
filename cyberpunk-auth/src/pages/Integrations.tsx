import React, { useState } from 'react';
import { Card, Switch, Button, Input, Modal, Typography, Tag, Form } from 'antd';
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
    { id: 'mcp-rag', name: 'RAG 服务', type: 'mcp', icon: <Server className="text-cyan-400" />, status: 'connected', description: '用于 RAG 操作的模型上下文协议服务器。', config: { endpoint: 'http://localhost:8080/mcp' } },
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

  const renderSection = (title: string, type: Integration['type']) => (
    <div className="mb-8">
      <Title level={4} className="!text-slate-300 !mb-4 flex items-center gap-2">
        <LinkIcon size={20} className="text-slate-500" />
        {title}
      </Title>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {integrations.filter(i => i.type === type).map(item => (
          <Card 
            key={item.id}
            className={`bg-slate-900/50 border-slate-800 backdrop-blur-sm hover:border-indigo-500/30 transition-all group ${item.status === 'active' || item.status === 'connected' ? 'border-l-4 border-l-green-500' : ''}`}
            actions={type === 'mcp' ? [] : undefined} // MCP uses internal inputs
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center border border-slate-700">
                  {item.icon}
                </div>
                <div>
                  <div className="text-slate-200 font-medium text-base">{item.name}</div>
                  {renderStatus(item.status)}
                </div>
              </div>
              
              {type === 'ci-cd' && (
                <Switch 
                  checked={item.status === 'active'} 
                  onChange={(checked) => handleToggle(item.id, checked)}
                  className="bg-slate-700"
                />
              )}
              
              {type === 'notification' && (
                 <Button 
                   size="small" 
                   icon={<Settings size={14} />} 
                   className="text-slate-400 hover:text-indigo-400 border-slate-700 hover:border-indigo-500 bg-transparent"
                   onClick={() => openConfig(item)}
                 >
                   Configure
                 </Button>
              )}
            </div>

            <Paragraph className="text-slate-400 text-sm h-10 mb-4 line-clamp-2">
              {item.description}
            </Paragraph>

            {type === 'mcp' && (
              <div className="mt-4 pt-4 border-t border-slate-800">
                 <div className="flex gap-2">
                    <Input 
                      size="small" 
                      placeholder="Endpoint URL" 
                      defaultValue={item.config?.endpoint as string | undefined} 
                      className="bg-slate-950 border-slate-700 text-slate-300 text-xs"
                      prefix={<Server size={12} className="text-slate-500" />}
                    />
                    <Button 
                      size="small" 
                      type={item.status === 'connected' ? 'default' : 'primary'}
                      className={item.status === 'connected' ? 'text-green-500 border-green-900/50 bg-green-900/10' : 'bg-indigo-600'}
                    >
                       {item.status === 'connected' ? 'Check' : 'Connect'}
                    </Button>
                 </div>
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );

  return (
    <div className="animate-fade-in">
      <div className="mb-6">
        <Title level={2} className="!text-slate-100 !mb-1 flex items-center gap-3">
          <LinkIcon className="text-cyan-400" />
          Integrations
        </Title>
        <Text className="text-slate-400">Manage connections to external tools, notification channels, and MCP servers.</Text>
      </div>

      {renderSection('CI/CD Pipelines', 'ci-cd')}
      {renderSection('Notification Channels', 'notification')}
      {renderSection('MCP Servers', 'mcp')}

      <Modal
        title={`Configure ${currentConfig?.name}`}
        open={isModalOpen}
        onOk={handleSaveConfig}
        onCancel={() => setIsModalOpen(false)}
        okText="Save Configuration"
        className="cyberpunk-modal"
      >
        <Form form={form} layout="vertical" className="mt-4">
          {currentConfig?.id === 'slack' && (
             <>
               <Form.Item name="webhookUrl" label="Webhook URL" rules={[{ required: true }]}>
                 <Input.Password placeholder="https://hooks.slack.com/services/..." />
               </Form.Item>
               <Form.Item name="channel" label="Default Channel">
                 <Input placeholder="#alerts" />
               </Form.Item>
             </>
          )}
          {currentConfig?.id === 'email' && (
             <Form.Item name="recipients" label="Recipients (comma separated)" rules={[{ required: true }]}>
               <Input.TextArea rows={3} placeholder="team@example.com, manager@example.com" />
             </Form.Item>
          )}
          {currentConfig?.id === 'dingtalk' && (
             <Form.Item name="accessToken" label="Access Token" rules={[{ required: true }]}>
               <Input.Password placeholder="Enter robot access token" />
             </Form.Item>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default Integrations;
