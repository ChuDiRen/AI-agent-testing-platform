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
    name: 'Alex Chen',
    email: 'alex.chen@cyberpunk.io',
    role: '工作空间管理员',
    avatar: 'https://i.pravatar.cc/150?u=me',
    bio: '高级自动化工程师，专注于 AI 驱动的测试框架。',
  });

  // Mock API Keys
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([
    {
      id: '1',
      name: 'CI/CD 流水线',
      prefix: 'cp_live_...',
      created: '2023-10-15',
      lastUsed: '2 分钟前',
      status: 'active',
    },
    {
      id: '2',
      name: '开发本地',
      prefix: 'cp_test_...',
      created: '2023-11-02',
      lastUsed: '1 天前',
      status: 'active',
    },
  ]);

  // Theme State
  const [theme, setTheme] = useState<'system' | 'light' | 'dark'>('dark');

  const handleUpdateProfile = (values: Partial<typeof user>) => {
    setLoading(true);
    setTimeout(() => {
      setUser({ ...user, ...values });
      setLoading(false);
      message.success('Profile updated successfully');
    }, 1000);
  };

  const generateApiKey = () => {
    const newKey: ApiKey = {
      id: Date.now().toString(),
      name: `New Key ${apiKeys.length + 1}`,
      prefix: 'cp_live_' + Math.random().toString(36).substring(7),
      created: new Date().toISOString().split('T')[0],
      lastUsed: 'Never',
      status: 'active',
    };
    setApiKeys([...apiKeys, newKey]);
    message.success('New API Key generated');
  };

  const deleteApiKey = (id: string) => {
    setApiKeys(apiKeys.filter(k => k.id !== id));
    message.success('API Key revoked');
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    message.success('Copied to clipboard');
  };

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <Text className="text-slate-300 font-medium">{text}</Text>,
    },
    {
      title: '令牌前缀',
      dataIndex: 'prefix',
      key: 'prefix',
      render: (text: string) => <Text code className="bg-slate-900 border-slate-700 text-slate-400">{text}</Text>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'red'} className="border-none">
          {status.toUpperCase()}
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
            className="text-slate-400 hover:text-neon-cyan" 
            onClick={() => copyToClipboard(record.prefix)}
          />
          <Button 
            type="text" 
            icon={<Trash2 size={16} />} 
            className="text-slate-400 hover:text-red-400" 
            onClick={() => deleteApiKey(record.id)} 
          />
        </Space>
      ),
    },
  ];

  return (
    <div className="animate-fade-in max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <Title level={2} className="!text-slate-100 !mb-1 flex items-center gap-3">
          <User className="text-neon-cyan" />
          User Profile Settings
        </Title>
        <Text className="text-slate-400">Manage your personal information, security credentials, and preferences.</Text>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Avatar & Theme */}
        <div className="space-y-6">
          {/* Avatar Card */}
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm">
            <div className="flex flex-col items-center text-center">
              <div className="relative group">
                <Avatar 
                  size={120} 
                  src={user.avatar} 
                  className="border-4 border-slate-800 shadow-2xl mb-4"
                />
                <div className="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                  <UploadIcon className="text-white" />
                </div>
              </div>
              <Title level={4} className="!text-slate-200 !mb-0">{user.name}</Title>
              <Text className="text-slate-500">{user.email}</Text>
              <Tag color="geekblue" className="mt-3 border-none bg-neon-cyan/10 text-neon-cyan">
                {user.role}
              </Tag>
              <Upload showUploadList={false}>
                <Button className="mt-6 border-slate-700 text-slate-300 hover:text-white hover:border-neon-cyan">
                  Change Avatar
                </Button>
              </Upload>
            </div>
          </Card>

          {/* Theme Preference */}
          <Card className="bg-slate-900/50 border-slate-800 backdrop-blur-sm" title={<span className="text-slate-200">Theme Preference</span>}>
            <Radio.Group 
              value={theme} 
              onChange={(e) => setTheme(e.target.value)} 
              className="w-full grid grid-cols-3 gap-2"
            >
              <Radio.Button 
                value="system" 
                className={`flex flex-col items-center justify-center h-24 border-slate-700 bg-slate-950/50 ${theme === 'system' ? '!border-neon-cyan !text-neon-cyan' : 'text-slate-500'}`}
              >
                <Monitor size={20} className="mb-2" />
                System
              </Radio.Button>
              <Radio.Button 
                value="light" 
                className={`flex flex-col items-center justify-center h-24 border-slate-700 bg-slate-950/50 ${theme === 'light' ? '!border-neon-cyan !text-neon-cyan' : 'text-slate-500'}`}
              >
                <Sun size={20} className="mb-2" />
                Light
              </Radio.Button>
              <Radio.Button 
                value="dark" 
                className={`flex flex-col items-center justify-center h-24 border-slate-700 bg-slate-950/50 ${theme === 'dark' ? '!border-neon-cyan !text-neon-cyan' : 'text-slate-500'}`}
              >
                <Moon size={20} className="mb-2" />
                Dark
              </Radio.Button>
            </Radio.Group>
          </Card>
        </div>

        {/* Right Column: Basic Info & API Keys */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <Card 
            className="bg-slate-900/50 border-slate-800 backdrop-blur-sm" 
            title={<span className="text-slate-200 flex items-center gap-2"><User size={18} /> Basic Information</span>}
          >
            <Form
              form={form}
              layout="vertical"
              initialValues={user}
              onFinish={handleUpdateProfile}
            >
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Form.Item label={<span className="text-slate-400">Full Name</span>} name="name" rules={[{ required: true }]}>
                  <Input className="bg-slate-950 border-slate-700 text-slate-200 focus:border-neon-cyan" />
                </Form.Item>
                <Form.Item label={<span className="text-slate-400">Email</span>} name="email" rules={[{ required: true, type: 'email' }]}>
                  <Input className="bg-slate-950 border-slate-700 text-slate-200 focus:border-neon-cyan" suffix={<Mail size={16} className="text-slate-600" />} />
                </Form.Item>
              </div>
              <Form.Item label={<span className="text-slate-400">Bio</span>} name="bio">
                <Input.TextArea rows={4} className="bg-slate-950 border-slate-700 text-slate-200 focus:border-neon-cyan" />
              </Form.Item>
              <div className="flex justify-end">
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  icon={<Save size={16} />}
                  className="bg-neon-cyan hover:bg-neon-cyan border-none h-10 px-6"
                >
                  Save Changes
                </Button>
              </div>
            </Form>
          </Card>

          {/* API Key Management */}
          <Card 
            className="bg-slate-900/50 border-slate-800 backdrop-blur-sm" 
            title={
              <div className="flex justify-between items-center">
                <span className="text-slate-200 flex items-center gap-2"><Key size={18} /> API Key Management</span>
                <Button 
                  type="primary" 
                  size="small" 
                  icon={<Plus size={14} />} 
                  onClick={generateApiKey}
                  className="bg-neon-cyan hover:bg-neon-cyan border-none"
                >
                  Generate New Key
                </Button>
              </div>
            }
          >
            <Paragraph className="text-slate-400 mb-6">
              These keys allow you to authenticate API requests programmatically. 
              <span className="text-amber-400 ml-1">Do not share your keys with anyone.</span>
            </Paragraph>
            
            <Table 
              dataSource={apiKeys} 
              columns={columns} 
              rowKey="id" 
              pagination={false}
              className="ant-table-cyberpunk"
            />
          </Card>
        </div>
      </div>
    </div>
  );
};

export default UserProfileSettings;

