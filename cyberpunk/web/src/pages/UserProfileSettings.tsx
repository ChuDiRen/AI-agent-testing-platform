import React, { useState } from 'react';
import {
  Typography,
  Card,
  Avatar,
  Button,
  Form,
  Input,
  Upload,
  Radio,
  Table,
  Tag,
  Space,
  message
} from 'antd';
import {
  User,
  Upload as UploadIcon,
  Key,
  Copy,
  Trash2,
  Plus,
  Moon,
  Sun,
  Monitor,
  Mail,
  Save
} from 'lucide-react';

const { Title, Text, Paragraph } = Typography;

interface ApiKey {
  id: string;
  name: string;
  prefix: string;
  created: string;
  lastUsed: string;
  status: 'active' | 'revoked';
}

export const UserProfileSettings: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  // Mock User Data
  const [user, setUser] = useState({
    name: '亚历克斯·陈',
    email: 'alex.chen@nexus.os',
    role: '工作空间管理员',
    avatar: 'https://i.pravatar.cc/150?u=me',
    bio: '资深自动化工程师，专注于 AI 驱动的测试框架。',
  });

  // Mock API Keys
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([
    {
      id: '1',
      name: 'CI/CD 流水线',
      prefix: 'nx_live_...',
      created: '2023-10-15',
      lastUsed: '2 分钟前',
      status: 'active',
    },
    {
      id: '2',
      name: '本地开发',
      prefix: 'nx_test_...',
      created: '2023-11-02',
      lastUsed: '1 天前',
      status: 'active',
    },
  ]);

  // Theme State
  const [theme, setTheme] = useState<'system' | 'light' | 'dark'>('light');

  const handleUpdateProfile = (values: Partial<typeof user>) => {
    setLoading(true);
    setTimeout(() => {
      setUser({ ...user, ...values });
      setLoading(false);
      message.success('个人资料更新成功');
    }, 1000);
  };

  const generateApiKey = () => {
    const newKey: ApiKey = {
      id: Date.now().toString(),
      name: `新密钥 ${apiKeys.length + 1}`,
      prefix: 'nx_live_' + Math.random().toString(36).substring(7),
      created: new Date().toISOString().split('T')[0],
      lastUsed: '从未使用',
      status: 'active',
    };
    setApiKeys([...apiKeys, newKey]);
    message.success('新 API 密钥已生成');
  };

  const deleteApiKey = (id: string) => {
    setApiKeys(apiKeys.filter(k => k.id !== id));
    message.success('API 密钥已撤销');
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    message.success('已复制到剪贴板');
  };

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: '令牌前缀',
      dataIndex: 'prefix',
      key: 'prefix',
      render: (text: string) => <Text code className="text-slate-500">{text}</Text>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'red'} className="border-none">
          {status === 'active' ? '活跃' : '已撤销'}
        </Tag>
      ),
    },
    {
      title: '最后使用',
      dataIndex: 'lastUsed',
      key: 'lastUsed',
      render: (text: string) => <Text className="text-slate-500">{text}</Text>,
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: unknown, record: ApiKey) => (
        <Space>
          <Button
            type="text"
            icon={<Copy size={16} />}
            className="text-slate-400 hover:text-blue-600"
            onClick={() => copyToClipboard(record.prefix)}
            title="复制"
          />
          <Button
            type="text"
            icon={<Trash2 size={16} />}
            className="text-slate-400 hover:text-red-500"
            onClick={() => deleteApiKey(record.id)}
            title="删除"
          />
        </Space>
      ),
    },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div>
        <Title level={2} className="!mb-1 flex items-center gap-3">
          <User className="text-blue-600" />
          用户个人资料设置
        </Title>
        <Text type="secondary">管理您的个人信息、安全凭据和偏好设置。</Text>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Avatar & Theme */}
        <div className="space-y-6">
          {/* Avatar Card */}
          <Card className="shadow-sm">
            <div className="flex flex-col items-center text-center">
              <div className="relative group">
                <Avatar
                  size={120}
                  src={user.avatar}
                  className="mb-4 shadow-md"
                />
                <div className="absolute inset-0 bg-black/40 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                  <UploadIcon className="text-white" />
                </div>
              </div>
              <Title level={4} className="!mb-0">{user.name}</Title>
              <Text type="secondary">{user.email}</Text>
              <Tag color="blue" className="mt-3 border-none bg-blue-50 text-blue-700">
                {user.role}
              </Tag>
              <Upload showUploadList={false}>
                <Button className="mt-6">
                  更改头像
                </Button>
              </Upload>
            </div>
          </Card>

          {/* Theme Preference */}
          <Card className="shadow-sm" title="主题偏好">
            <Radio.Group
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              className="w-full grid grid-cols-3 gap-2"
            >
              <Radio.Button
                value="system"
                className="flex flex-col items-center justify-center h-20 text-slate-500"
              >
                <Monitor size={20} className="mb-2" />
                系统
              </Radio.Button>
              <Radio.Button
                value="light"
                className="flex flex-col items-center justify-center h-20 text-slate-500"
              >
                <Sun size={20} className="mb-2" />
                浅色
              </Radio.Button>
              <Radio.Button
                value="dark"
                className="flex flex-col items-center justify-center h-20 text-slate-500"
              >
                <Moon size={20} className="mb-2" />
                深色
              </Radio.Button>
            </Radio.Group>
          </Card>
        </div>

        {/* Right Column: Basic Info & API Keys */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <Card
            className="shadow-sm"
            title={<span className="flex items-center gap-2"><User size={18} /> 基本信息</span>}
          >
            <Form
              form={form}
              layout="vertical"
              initialValues={user}
              onFinish={handleUpdateProfile}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Form.Item label="全名" name="name" rules={[{ required: true, message: '请输入您的全名' }]}>
                  <Input prefix={<User size={16} className="text-slate-400" />} />
                </Form.Item>
                <Form.Item label="邮箱地址" name="email" rules={[{ required: true, type: 'email', message: '请输入有效的邮箱地址' }]}>
                  <Input suffix={<Mail size={16} className="text-slate-400" />} />
                </Form.Item>
              </div>
              <Form.Item label="个人简介" name="bio">
                <Input.TextArea rows={4} showCount maxLength={200} placeholder="简短介绍一下您自己..." />
              </Form.Item>
              <div className="flex justify-end">
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  icon={<Save size={16} />}
                >
                  保存更改
                </Button>
              </div>
            </Form>
          </Card>

          {/* API Key Management */}
          <Card
            className="shadow-sm"
            title={
              <div className="flex justify-between items-center">
                <span className="flex items-center gap-2"><Key size={18} /> API 密钥管理</span>
                <Button
                  type="primary"
                  ghost
                  size="small"
                  icon={<Plus size={14} />}
                  onClick={generateApiKey}
                >
                  生成新密钥
                </Button>
              </div>
            }
          >
            <Paragraph type="secondary" className="mb-6">
              这些密钥允许您以编程方式通过 API 请求进行身份验证。
              <Text type="warning" className="ml-1">请勿将您的密钥泄露给任何人。</Text>
            </Paragraph>

            <Table
              dataSource={apiKeys}
              columns={columns}
              rowKey="id"
              pagination={false}
            />
          </Card>
        </div>
      </div>
    </div>
  );
};

export default UserProfileSettings;
