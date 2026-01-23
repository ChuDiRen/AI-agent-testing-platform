import React, { useState } from 'react';
import { Tabs, Table, Input, Button, Space, Upload, message, Popconfirm } from 'antd';
import { Eye, EyeOff, Trash2, Plus, Upload as UploadIcon, Download, Save, Globe, Server, Database, Cloud } from 'lucide-react';
import type { UploadProps } from 'antd';
import type { RcFile } from 'antd/es/upload';
import { Card } from '../components/ui/Card';

interface EnvVariable {
  key: string;
  name: string;
  value: string;
  description: string;
  isSecret?: boolean;
}

interface EnvTableProps {
  environment: string;
  initialData: EnvVariable[];
}

const EnvTable: React.FC<EnvTableProps> = ({ environment, initialData }) => {
  const [data, setData] = useState<EnvVariable[]>(initialData);
  const [visibleSecrets, setVisibleSecrets] = useState<Record<string, boolean>>({});

  const handleAdd = () => {
    const newVar: EnvVariable = {
      key: Date.now().toString(),
      name: '',
      value: '',
      description: '',
      isSecret: false,
    };
    setData([...data, newVar]);
  };

  const handleDelete = (key: string) => {
    setData(data.filter(item => item.key !== key));
  };

  const handleChange = (key: string, field: keyof EnvVariable, value: string | boolean) => {
    const newData = data.map(item => {
      if (item.key === key) {
        return { ...item, [field]: value };
      }
      return item;
    });
    setData(newData);
  };

  const toggleVisibility = (key: string) => {
    setVisibleSecrets((prev: Record<string, boolean>) => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const handleExport = () => {
    const content = data
      .filter(item => item.name)
      .map(item => `${item.name}=${item.value}${item.description ? ` # ${item.description}` : ''}`)
      .join('\n');

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `.env.${environment.toLowerCase()}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    message.success(`已导出 .env.${environment.toLowerCase()}`);
  };

  const handleImport: UploadProps['beforeUpload'] = (file) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      const lines = content.split('\n');
      const newVars: EnvVariable[] = [];

      lines.forEach((line, index) => {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) return;

        const [keyVal, ...descParts] = trimmed.split('#');
        const [name, ...valParts] = keyVal.split('=');

        if (name) {
          newVars.push({
            key: `${Date.now()}-${index}`,
            name: name.trim(),
            value: valParts.join('=').trim(),
            description: descParts.join('#').trim(),
            isSecret: name.trim().toLowerCase().includes('secret') || name.trim().toLowerCase().includes('password') || name.trim().toLowerCase().includes('key'),
          });
        }
      });

      setData([...data, ...newVars]);
      message.success(`已导入 ${newVars.length} 个变量`);
    };
    reader.readAsText(file as RcFile);
    return false;
  };

  const columns = [
    {
      title: '键 (Key)',
      dataIndex: 'name',
      width: '30%',
      render: (text: string, record: EnvVariable) => (
        <Input
          placeholder="例如: API_KEY"
          value={text}
          onChange={e => handleChange(record.key, 'name', e.target.value)}
          className="font-mono text-slate-600"
        />
      ),
    },
    {
      title: '值 (Value)',
      dataIndex: 'value',
      width: '35%',
      render: (text: string, record: EnvVariable) => (
        <Input
          type={visibleSecrets[record.key] ? 'text' : 'password'}
          placeholder="变量值"
          value={text}
          onChange={e => handleChange(record.key, 'value', e.target.value)}
          suffix={
            <Button
              type="text"
              size="small"
              icon={visibleSecrets[record.key] ? <EyeOff size={14} /> : <Eye size={14} />}
              onClick={() => toggleVisibility(record.key)}
              className="text-slate-400 hover:text-slate-600"
            />
          }
          className="font-mono text-slate-600"
        />
      ),
    },
    {
      title: '描述',
      dataIndex: 'description',
      width: '25%',
      render: (text: string, record: EnvVariable) => (
        <Input
          placeholder="可选描述"
          value={text}
          onChange={e => handleChange(record.key, 'description', e.target.value)}
          className="text-slate-500"
        />
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: '10%',
      render: (_: unknown, record: EnvVariable) => (
        <Popconfirm title="确定要删除此变量吗？" onConfirm={() => handleDelete(record.key)} okText="确定" cancelText="取消">
          <Button
            type="text"
            danger
            icon={<Trash2 size={16} />}
          />
        </Popconfirm>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <Space>
          <Upload beforeUpload={handleImport} showUploadList={false} accept=".env">
            <Button icon={<UploadIcon size={16} />}>
              导入 .env
            </Button>
          </Upload>
          <Button icon={<Download size={16} />} onClick={handleExport}>
            导出
          </Button>
        </Space>
        <Button type="primary" icon={<Save size={16} />}>
          保存更改
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="key"
        pagination={false}
        locale={{ emptyText: '未定义环境变量' }}
      />

      <Button
        type="dashed"
        block
        onClick={handleAdd}
        icon={<Plus size={16} />}
        className="mt-4 text-slate-500 border-slate-300 hover:border-blue-400 hover:text-blue-500"
      >
        添加变量
      </Button>
    </div>
  );
};

// Mock Data
const MOCK_GLOBAL_VARS: EnvVariable[] = [
  { key: '1', name: 'APP_NAME', value: 'Nexus 平台', description: '应用名称', isSecret: false },
  { key: '2', name: 'LOG_LEVEL', value: 'debug', description: '全局日志级别', isSecret: false },
];

const MOCK_DEV_VARS: EnvVariable[] = [
  { key: '1', name: 'API_URL', value: 'http://localhost:3000', description: '本地 API 端点', isSecret: false },
  { key: '2', name: 'DB_HOST', value: 'localhost', description: '本地数据库', isSecret: false },
  { key: '3', name: 'DB_PASSWORD', value: 'secret_dev_pass', description: '数据库密码', isSecret: true },
];

const MOCK_STAGING_VARS: EnvVariable[] = [
  { key: '1', name: 'API_URL', value: 'https://staging-api.nexus.os', description: '测试环境 API 端点', isSecret: false },
  { key: '2', name: 'DB_HOST', value: 'staging-db.nexus.os', description: '测试环境数据库', isSecret: false },
  { key: '3', name: 'DB_PASSWORD', value: 'complex_staging_pass_123', description: '数据库密码', isSecret: true },
];

const MOCK_PROD_VARS: EnvVariable[] = [
  { key: '1', name: 'API_URL', value: 'https://api.nexus.os', description: '生产环境 API 端点', isSecret: false },
  { key: '2', name: 'DB_HOST', value: 'prod-db-cluster.aws.com', description: '生产环境数据库集群', isSecret: false },
  { key: '3', name: 'DB_PASSWORD', value: 'very_secure_prod_pass_!@#', description: '数据库密码', isSecret: true },
  { key: '4', name: 'STRIPE_KEY', value: 'sk_live_51Hz...', description: 'Stripe 密钥', isSecret: true },
];

export const EnvironmentSettings: React.FC = () => {
  const items = [
    {
      key: 'global',
      label: (
        <span className="flex items-center gap-2">
          <Globe size={16} />
          全局
        </span>
      ),
      children: <EnvTable environment="Global" initialData={MOCK_GLOBAL_VARS} />,
    },
    {
      key: 'dev',
      label: (
        <span className="flex items-center gap-2">
          <Database size={16} />
          开发环境 (Dev)
        </span>
      ),
      children: <EnvTable environment="Dev" initialData={MOCK_DEV_VARS} />,
    },
    {
      key: 'staging',
      label: (
        <span className="flex items-center gap-2">
          <Server size={16} />
          测试环境 (Staging)
        </span>
      ),
      children: <EnvTable environment="Staging" initialData={MOCK_STAGING_VARS} />,
    },
    {
      key: 'prod',
      label: (
        <span className="flex items-center gap-2">
          <Cloud size={16} />
          生产环境 (Prod)
        </span>
      ),
      children: <EnvTable environment="Prod" initialData={MOCK_PROD_VARS} />,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">环境设置</h1>
        <p className="text-slate-500 mt-1">管理不同部署阶段的环境变量和机密信息</p>
      </div>

      <Card className="min-h-[600px]">
        <Tabs
          defaultActiveKey="dev"
          items={items}
        />
      </Card>
    </div>
  );
};
