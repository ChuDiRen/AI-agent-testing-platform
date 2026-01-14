import React, { useState } from 'react';
import { Tabs, Table, Input, Button, Space, Upload, message, Popconfirm } from 'antd';
import { Eye, EyeOff, Trash2, Plus, Upload as UploadIcon, Download, Save, Globe, Server, Database, Cloud } from 'lucide-react';
import type { UploadProps } from 'antd';
import type { RcFile } from 'antd/es/upload';

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
    message.success(`Exported .env.${environment.toLowerCase()}`);
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
      message.success(`Imported ${newVars.length} variables`);
    };
    reader.readAsText(file as RcFile);
    return false;
  };

  const columns = [
    {
      title: '键',
      dataIndex: 'name',
      width: '30%',
      render: (text: string, record: EnvVariable) => (
        <Input 
          placeholder="例如 API_KEY" 
          value={text} 
          onChange={e => handleChange(record.key, 'name', e.target.value)}
          className="font-mono text-slate-300 bg-slate-900/50 border-slate-700 focus:border-neon-cyan"
        />
      ),
    },
    {
      title: '值',
      dataIndex: 'value',
      width: '35%',
      render: (text: string, record: EnvVariable) => (
        <Input
          type={visibleSecrets[record.key] ? 'text' : 'password'}
          placeholder="值"
          value={text}
          onChange={e => handleChange(record.key, 'value', e.target.value)}
          suffix={
            <Button
              type="text"
              size="small"
              icon={visibleSecrets[record.key] ? <EyeOff size={14} /> : <Eye size={14} />}
              onClick={() => toggleVisibility(record.key)}
              className="text-slate-500 hover:text-slate-300"
            />
          }
          className="font-mono text-slate-300 bg-slate-900/50 border-slate-700 focus:border-neon-cyan"
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
          className="text-slate-400 bg-slate-900/50 border-slate-700 focus:border-neon-cyan"
        />
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: '10%',
      render: (_: unknown, record: EnvVariable) => (
        <Popconfirm title="Delete this variable?" onConfirm={() => handleDelete(record.key)}>
          <Button 
            type="text" 
            danger 
            icon={<Trash2 size={16} />} 
            className="hover:bg-red-500/10"
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
             <Button icon={<UploadIcon size={16} />} className="border-slate-600 text-slate-300 hover:text-neon-cyan hover:border-neon-cyan">
               Import .env
             </Button>
           </Upload>
           <Button icon={<Download size={16} />} onClick={handleExport} className="border-slate-600 text-slate-300 hover:text-neon-cyan hover:border-neon-cyan">
             Export
           </Button>
        </Space>
        <Button type="primary" icon={<Save size={16} />} className="bg-neon-cyan hover:bg-neon-cyan border-none">
          Save Changes
        </Button>
      </div>
      
      <Table
        columns={columns}
        dataSource={data}
        rowKey="key"
        pagination={false}
        className="cyberpunk-table"
        locale={{ emptyText: 'No environment variables defined' }}
      />
      
      <Button 
        type="dashed" 
        block 
        onClick={handleAdd} 
        icon={<Plus size={16} />}
        className="mt-4 border-slate-700 text-slate-400 hover:text-neon-cyan hover:border-neon-cyan bg-slate-800/30"
      >
        Add Variable
      </Button>

      <style>{`
        .cyberpunk-table .ant-table {
          background: transparent !important;
        }
        .cyberpunk-table .ant-table-thead > tr > th {
          background: rgba(30, 41, 59, 0.5) !important;
          color: #94a3b8 !important;
          border-bottom: 1px solid rgba(71, 85, 105, 0.5) !important;
        }
        .cyberpunk-table .ant-table-tbody > tr > td {
          border-bottom: 1px solid rgba(51, 65, 85, 0.3) !important;
          padding: 12px 16px !important;
        }
        .cyberpunk-table .ant-table-tbody > tr:hover > td {
          background: rgba(51, 65, 85, 0.3) !important;
        }
        .cyberpunk-table .ant-input {
          transition: all 0.3s;
        }
        .cyberpunk-table .ant-input:hover, .cyberpunk-table .ant-input:focus {
          background: rgba(15, 23, 42, 0.8) !important;
        }
      `}</style>
    </div>
  );
};

// Mock Data
const MOCK_GLOBAL_VARS: EnvVariable[] = [
  { key: '1', name: 'APP_NAME', value: 'Cyberpunk Auth', description: 'Application Name', isSecret: false },
  { key: '2', name: 'LOG_LEVEL', value: 'debug', description: 'Global logging level', isSecret: false },
];

const MOCK_DEV_VARS: EnvVariable[] = [
  { key: '1', name: 'API_URL', value: 'http://localhost:3000', description: 'Local API Endpoint', isSecret: false },
  { key: '2', name: 'DB_HOST', value: 'localhost', description: 'Local Database', isSecret: false },
  { key: '3', name: 'DB_PASSWORD', value: 'secret_dev_pass', description: 'Database Password', isSecret: true },
];

const MOCK_STAGING_VARS: EnvVariable[] = [
  { key: '1', name: 'API_URL', value: 'https://staging-api.cyberpunk.com', description: 'Staging API Endpoint', isSecret: false },
  { key: '2', name: 'DB_HOST', value: 'staging-db.cyberpunk.com', description: 'Staging Database', isSecret: false },
  { key: '3', name: 'DB_PASSWORD', value: 'complex_staging_pass_123', description: 'Database Password', isSecret: true },
];

const MOCK_PROD_VARS: EnvVariable[] = [
  { key: '1', name: 'API_URL', value: 'https://api.cyberpunk.com', description: 'Production API Endpoint', isSecret: false },
  { key: '2', name: 'DB_HOST', value: 'prod-db-cluster.aws.com', description: 'Production Database', isSecret: false },
  { key: '3', name: 'DB_PASSWORD', value: 'very_secure_prod_pass_!@#', description: 'Database Password', isSecret: true },
  { key: '4', name: 'STRIPE_KEY', value: 'sk_live_51Hz...', description: 'Stripe Secret Key', isSecret: true },
];

export const EnvironmentSettings: React.FC = () => {
  const items = [
    {
      key: 'global',
      label: (
        <span className="flex items-center gap-2">
          <Globe size={16} />
          Global
        </span>
      ),
      children: <EnvTable environment="Global" initialData={MOCK_GLOBAL_VARS} />,
    },
    {
      key: 'dev',
      label: (
        <span className="flex items-center gap-2">
          <Database size={16} />
          Development
        </span>
      ),
      children: <EnvTable environment="Dev" initialData={MOCK_DEV_VARS} />,
    },
    {
      key: 'staging',
      label: (
        <span className="flex items-center gap-2">
          <Server size={16} />
          Staging
        </span>
      ),
      children: <EnvTable environment="Staging" initialData={MOCK_STAGING_VARS} />,
    },
    {
      key: 'prod',
      label: (
        <span className="flex items-center gap-2">
          <Cloud size={16} />
          Production
        </span>
      ),
      children: <EnvTable environment="Prod" initialData={MOCK_PROD_VARS} />,
    },
  ];

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Environment Settings</h1>
        <p className="text-slate-400">Manage environment variables and secrets across different deployment stages</p>
      </div>

      <div className="bg-slate-800/50 border border-slate-700/50 rounded-lg p-6 backdrop-blur-sm min-h-[600px]">
        <Tabs 
          defaultActiveKey="dev" 
          items={items} 
          className="cyberpunk-tabs"
        />
      </div>

      <style>{`
        .cyberpunk-tabs .ant-tabs-nav::before {
          border-bottom: 1px solid rgba(71, 85, 105, 0.5);
        }
        .cyberpunk-tabs .ant-tabs-tab {
          color: #94a3b8;
          transition: all 0.3s;
        }
        .cyberpunk-tabs .ant-tabs-tab:hover {
          color: #818cf8;
        }
        .cyberpunk-tabs .ant-tabs-tab.ant-tabs-tab-active .ant-tabs-tab-btn {
          color: #818cf8;
          text-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
        }
        .cyberpunk-tabs .ant-tabs-ink-bar {
          background: #818cf8;
          height: 2px;
          box-shadow: 0 0 10px rgba(99, 102, 241, 0.8);
        }
      `}</style>
    </div>
  );
};

