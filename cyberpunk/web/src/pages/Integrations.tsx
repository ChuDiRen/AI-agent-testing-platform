import React, { useState } from 'react';
import { Card, Switch, Button, Input, Modal, Typography, Tag, Form } from 'antd';
import { motion } from 'framer-motion';
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
    { id: 'jenkins', name: 'Jenkins', type: 'ci-cd', icon: <GitBranch className="text-orange-500" />, status: 'active', description: '从 Jenkins 流水线触发构建并获取产物。' },
    { id: 'github', name: 'GitHub Actions', type: 'ci-cd', icon: <Github className="text-slate-800" />, status: 'inactive', description: '同步工作流运行状态和状态检查。' },
    { id: 'gitlab', name: 'GitLab CI', type: 'ci-cd', icon: <Gitlab className="text-orange-600" />, status: 'inactive', description: '集成 GitLab CI/CD 流水线。' },
    { id: 'slack', name: 'Slack', type: 'notification', icon: <Slack className="text-purple-500" />, status: 'active', description: '将测试结果和告警发送到 Slack 频道。' },
    { id: 'dingtalk', name: '钉钉 (DingTalk)', type: 'notification', icon: <MessageSquare className="text-blue-500" />, status: 'inactive', description: '通过钉钉机器人消息通知团队。' },
    { id: 'email', name: '邮件 (Email)', type: 'notification', icon: <Mail className="text-amber-500" />, status: 'active', description: '将摘要报告发送到邮件列表。' },
    { id: 'mcp-rag', name: 'RAG 服务', type: 'mcp', icon: <Server className="text-blue-600" />, status: 'connected', description: '用于 RAG 操作的模型上下文协议 (MCP) 服务器。', config: { endpoint: 'http://localhost:8080/mcp' } },
    { id: 'mcp-chart', name: '图表服务', type: 'mcp', icon: <Server className="text-pink-500" />, status: 'disconnected', description: '用于图表生成和分析的 MCP 服务器。', config: { endpoint: 'http://localhost:8081/mcp' } },
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
    switch (status) {
      case 'active': return <Tag color="success">已启用</Tag>;
      case 'inactive': return <Tag color="default">未启用</Tag>;
      case 'connected': return <Tag color="success" icon={<CheckCircle size={12} />}>已连接</Tag>;
      case 'disconnected': return <Tag color="error" icon={<XCircle size={12} />}>已断开</Tag>;
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
      <Title level={4} className="!text-slate-700 !mb-4 flex items-center gap-2 tracking-tight">
        <LinkIcon size={20} className="text-slate-500" />
        {title}
      </Title>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {integrations.filter(i => i.type === type).map((item) => (
          <Card
            key={item.id}
            bordered={false}
            className={`
              h-full flex flex-col shadow-sm cursor-default hover:shadow-md transition-shadow
              border border-slate-200
            `}
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-slate-50 flex items-center justify-center border border-slate-200">
                  {item.icon}
                </div>
                <div>
                  <div className="text-slate-800 font-medium text-base">{item.name}</div>
                  {renderStatus(item.status)}
                </div>
              </div>

              {type === 'ci-cd' && (
                <Switch
                  checked={item.status === 'active'}
                  onChange={(checked) => handleToggle(item.id, checked)}
                />
              )}

              {type === 'notification' && (
                <Button
                  size="small"
                  icon={<Settings size={14} />}
                  className="text-slate-400 hover:text-blue-600 border-slate-200"
                  onClick={() => openConfig(item)}
                >
                  配置
                </Button>
              )}
            </div>

            <Paragraph className="text-slate-500 text-sm h-10 mb-4 line-clamp-2 leading-relaxed">
              {item.description}
            </Paragraph>

            {type === 'mcp' && (
              <div className="mt-auto pt-4 border-t border-slate-100">
                <div className="flex gap-2">
                  <Input
                    size="small"
                    placeholder="端点 URL"
                    defaultValue={item.config?.endpoint as string | undefined}
                    className="text-xs font-mono"
                    prefix={<Server size={12} className="text-slate-400" />}
                  />
                  <Button
                    size="small"
                    type={item.status === 'connected' ? 'default' : 'primary'}
                    className={
                      item.status === 'connected'
                        ? 'text-emerald-600 border-emerald-200 bg-emerald-50 font-mono text-xs'
                        : 'bg-blue-600 border-none font-bold font-mono text-xs hover:bg-blue-500'
                    }
                  >
                    {item.status === 'connected' ? '检查' : '连接'}
                  </Button>
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>
    </motion.div>
  );

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6 max-w-7xl mx-auto p-6"
    >
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="mb-6"
      >
        <Title level={2} className="!text-slate-900 !mb-1 flex items-center gap-3 tracking-tight">
          <LinkIcon className="text-blue-600" />
          第三方集成
        </Title>
        <Text className="text-slate-500 text-sm">管理与外部工具、通知频道和 MCP 服务器的连接。</Text>
      </motion.div>

      {renderSection('CI/CD 流水线', 'ci-cd', 0.2)}
      {renderSection('通知频道', 'notification', 0.3)}
      {renderSection('MCP 服务器', 'mcp', 0.4)}

      <Modal
        title={`配置 ${currentConfig?.name}`}
        open={isModalOpen}
        onOk={handleSaveConfig}
        onCancel={() => setIsModalOpen(false)}
        okText="保存配置"
        cancelText="取消"
      >
        <Form form={form} layout="vertical" className="mt-4">
          {currentConfig?.id === 'slack' && (
            <>
              <Form.Item name="webhookUrl" label="Webhook URL" rules={[{ required: true, message: '请输入 Webhook URL' }]}>
                <Input.Password placeholder="https://hooks.slack.com/services/..." />
              </Form.Item>
              <Form.Item name="channel" label="默认频道">
                <Input placeholder="#alerts" />
              </Form.Item>
            </>
          )}
          {currentConfig?.id === 'email' && (
            <Form.Item name="recipients" label="收件人" rules={[{ required: true, message: '请输入收件人' }]}>
              <Input.TextArea rows={3} placeholder="team@example.com, manager@example.com" />
            </Form.Item>
          )}
          {currentConfig?.id === 'dingtalk' && (
            <Form.Item name="accessToken" label="访问令牌 (Access Token)" rules={[{ required: true, message: '请输入访问令牌' }]}>
              <Input.Password placeholder="输入机器人访问令牌" />
            </Form.Item>
          )}
        </Form>
      </Modal>
    </motion.div>
  );
};

export default Integrations;
