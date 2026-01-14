import React, { useState } from 'react';
import { Table, Tag, Button, Input, Select, Space, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { 
  Search, Plus, Trash2, Play, FileCode, 
  MoreHorizontal, User, Calendar, CheckCircle, 
  XCircle, AlertCircle, Clock
} from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { motion } from 'framer-motion';
import { CyberCard } from '../components/CyberCard';

// Types
interface TestCase {
  id: string;
  name: string;
  tag: 'Functional' | 'Security' | 'Performance' | 'Integration';
  api: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  status: 'Passed' | 'Failed' | 'Skipped' | 'Pending';
  creator: string;
  lastRun: string;
  codeSnippet: string;
}

// Mock Data
const MOCK_TEST_CASES: TestCase[] = [
  {
    id: 'TC-001',
    name: '验证有效凭据的登录',
    tag: 'Functional',
    api: '/auth/login',
    method: 'POST',
    status: 'Passed',
    creator: 'Neo',
    lastRun: '2024-03-15 10:30',
    codeSnippet: `test('应该成功登录', async () => {
  const response = await client.post('/auth/login', {
    username: 'neo@matrix.com',
    password: 'password123'
  });
  expect(response.status).toBe(200);
  expect(response.data).toHaveProperty('token');
});`
  },
  {
    id: 'TC-002',
    name: 'SQL 注入漏洞检查',
    tag: 'Security',
    api: '/users/search',
    method: 'GET',
    status: 'Pending',
    creator: 'Trinity',
    lastRun: '-',
    codeSnippet: `test('应该防止 SQL 注入', async () => {
  const response = await client.get('/users/search?q=admin" OR 1=1--');
  expect(response.status).toBe(400); // 应该被拒绝
});`
  },
  {
    id: 'TC-003',
    name: '创建发票验证',
    tag: 'Functional',
    api: '/invoices',
    method: 'POST',
    status: 'Failed',
    creator: 'Morpheus',
    lastRun: '2024-03-14 15:45',
    codeSnippet: `test('应该验证发票金额', async () => {
  const response = await client.post('/invoices', {
    amount: -100, // 无效
    currency: 'USD'
  });
  expect(response.status).toBe(400);
  expect(response.data.error).toBe('无效金额');
});`
  },
  {
    id: 'TC-004',
    name: '获取用户配置文件性能',
    tag: 'Performance',
    api: '/users/me',
    method: 'GET',
    status: 'Passed',
    creator: 'Neo',
    lastRun: '2024-03-15 09:15',
    codeSnippet: `test('应该在 200ms 内响应', async () => {
  const start = Date.now();
  await client.get('/users/me');
  const duration = Date.now() - start;
  expect(duration).toBeLessThan(200);
});`
  },
  {
    id: 'TC-005',
    name: '令牌过期处理',
    tag: 'Security',
    api: '/auth/refresh',
    method: 'POST',
    status: 'Skipped',
    creator: 'Trinity',
    lastRun: '2024-03-10 11:00',
    codeSnippet: `test('应该拒绝过期的令牌', async () => {
  // 设置过期的令牌
  const response = await client.post('/auth/refresh', {}, {
    headers: { Authorization: 'Bearer expired_token' }
  });
  expect(response.status).toBe(401);
});`
  }
];

export const TestCaseManagement: React.FC = () => {
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);
  const [filterTag, setFilterTag] = useState<string | null>(null);
  const [searchText, setSearchText] = useState('');

  const onSelectChange = (newSelectedRowKeys: React.Key[]) => {
    setSelectedRowKeys(newSelectedRowKeys);
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: onSelectChange,
  };

  const handleBatchAction = (action: string) => {
    message.success(`${action} applied to ${selectedRowKeys.length} items`);
    setSelectedRowKeys([]);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Passed': return <CheckCircle size={14} />;
      case 'Failed': return <XCircle size={14} />;
      case 'Pending': return <Clock size={14} />;
      case 'Skipped': return <AlertCircle size={14} />;
      default: return null;
    }
  };

  const columns: ColumnsType<TestCase> = [
    {
      title: 'Case ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
      render: (text) => <span className="font-mono text-slate-400">{text}</span>,
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text) => <span className="font-medium text-slate-200">{text}</span>,
    },
    {
      title: 'Tag',
      dataIndex: 'tag',
      key: 'tag',
      width: 120,
      render: (tag) => {
        let color = 'default';
        if (tag === 'Functional') color = 'blue';
        if (tag === 'Security') color = 'purple';
        if (tag === 'Performance') color = 'orange';
        return <Tag color={color} className="border-none">{tag}</Tag>;
      }
    },
    {
      title: 'Associated API',
      key: 'api',
      width: 200,
      render: (_, record) => (
        <Space size="small">
          <Tag className={`
            font-mono font-bold border-none 
            ${record.method === 'GET' ? 'text-blue-400 bg-blue-400/10' : 
              record.method === 'POST' ? 'text-green-400 bg-green-400/10' : 
              record.method === 'DELETE' ? 'text-red-400 bg-red-400/10' : 
              'text-orange-400 bg-orange-400/10'}
          `}>
            {record.method}
          </Tag>
          <span className="font-mono text-xs text-slate-400">{record.api}</span>
        </Space>
      ),
    },
    {
      title: 'Last Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => (
        <Space size={4} className={`
          ${status === 'Passed' ? 'text-green-400' : 
            status === 'Failed' ? 'text-red-400' : 
            status === 'Pending' ? 'text-yellow-400' : 'text-slate-400'}
        `}>
          {getStatusIcon(status)}
          <span>{status}</span>
        </Space>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 100,
      render: () => (
        <Button type="text" icon={<MoreHorizontal size={16} className="text-slate-400" />} />
      ),
    },
  ];

  const filteredData = MOCK_TEST_CASES.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchText.toLowerCase()) || 
                          item.id.toLowerCase().includes(searchText.toLowerCase());
    const matchesStatus = filterStatus ? item.status === filterStatus : true;
    const matchesTag = filterTag ? item.tag === filterTag : true;
    return matchesSearch && matchesStatus && matchesTag;
  });

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="p-6 space-y-6"
    >
      {/* Header */}
      <div className="flex justify-between items-center">
        <motion.div
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-3xl font-bold font-display text-white mb-1 drop-shadow-md">Test Case Management</h1>
          <p className="text-slate-400 font-mono text-sm">Manage, organize and execute your test suites</p>
        </motion.div>
        <motion.div 
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="flex gap-3"
        >
          <Button icon={<Play size={16} />} className="cyber-button-secondary">
            Run Suite
          </Button>
          <Button type="primary" icon={<Plus size={16} />} className="cyber-button">
            New Test Case
          </Button>
        </motion.div>
      </div>

      {/* Filter Bar */}
      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="p-4 bg-slate-900/40 border border-slate-700/50 rounded-lg flex flex-wrap gap-4 items-center backdrop-blur-md shadow-lg"
      >
        <Input 
          prefix={<Search size={14} className="text-slate-500" />} 
          placeholder="Search cases..." 
          className="w-64 bg-slate-900/50 border-slate-700 hover:border-neon-cyan focus:border-neon-cyan"
          value={searchText}
          onChange={e => setSearchText(e.target.value)}
        />
        
        <Select 
          placeholder="Status" 
          allowClear 
          className="w-32"
          onChange={setFilterStatus}
          options={[
            { value: 'Passed', label: 'Passed' },
            { value: 'Failed', label: 'Failed' },
            { value: 'Pending', label: 'Pending' },
            { value: 'Skipped', label: 'Skipped' },
          ]}
        />

        <Select 
          placeholder="Tag" 
          allowClear 
          className="w-32"
          onChange={setFilterTag}
          options={[
            { value: 'Functional', label: 'Functional' },
            { value: 'Security', label: 'Security' },
            { value: 'Performance', label: 'Performance' },
          ]}
        />
      </motion.div>

      {/* Batch Actions */}
      {selectedRowKeys.length > 0 && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-4 p-3 bg-neon-cyan/10 border border-neon-cyan/30 rounded-lg text-neon-cyan shadow-[0_0_15px_rgba(0,243,255,0.2)]"
        >
          <span className="font-medium font-mono">{selectedRowKeys.length} selected</span>
          <div className="h-4 w-px bg-neon-cyan/20" />
          <Button 
            size="small" 
            type="text" 
            className="text-neon-cyan hover:text-white hover:bg-neon-cyan/20 font-bold"
            onClick={() => handleBatchAction('Added to Suite')}
          >
            Add to Suite
          </Button>
          <Button 
            size="small" 
            type="text" 
            danger
            icon={<Trash2 size={14} />}
            onClick={() => handleBatchAction('Deleted')}
          >
            Delete
          </Button>
        </motion.div>
      )}

      {/* Table */}
      <CyberCard className="!p-0 overflow-hidden" delay={0.3}>
        <Table
          rowSelection={rowSelection}
          columns={columns}
          dataSource={filteredData}
          rowKey="id"
          expandable={{
            expandedRowRender: (record) => (
              <div className="p-4 bg-slate-950/50 border-t border-slate-800/50">
                <div className="flex items-center gap-2 mb-2 text-neon-cyan text-xs uppercase tracking-wider font-bold font-display">
                  <FileCode size={12} />
                  Test Implementation
                </div>
                <div className="rounded-md overflow-hidden border border-slate-800 shadow-inner">
                  <SyntaxHighlighter
                    language="javascript"
                    style={vscDarkPlus as unknown as Record<string, React.CSSProperties>}
                    customStyle={{ margin: 0, background: '#050505', padding: '1rem' }}
                    showLineNumbers={true}
                  >
                    {record.codeSnippet}
                  </SyntaxHighlighter>
                </div>
                <div className="mt-4 flex gap-4 text-xs text-slate-500 font-mono">
                  <span className="flex items-center gap-1">
                    <User size={12} /> Created by {record.creator}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar size={12} /> Last run: {record.lastRun}
                  </span>
                </div>
              </div>
            ),
            expandIcon: ({ expanded, onExpand, record }) => (
               <Button 
                 type="text" 
                 size="small"
                 onClick={e => onExpand(record, e)}
                 className="text-slate-500 hover:text-neon-cyan transition-colors"
               >
                 {expanded ? 'Hide' : 'Code'}
               </Button>
            ),
            columnTitle: 'Code'
          }}
          pagination={{ pageSize: 10 }}
          className="cyberpunk-table"
        />
      </CyberCard>

      <style>{`
        .cyberpunk-table .ant-table {
          background: transparent !important;
        }
        .cyberpunk-table .ant-table-thead > tr > th {
          background: rgba(15, 23, 42, 0.8) !important;
          color: #94a3b8 !important;
          border-bottom: 1px solid rgba(51, 65, 85, 0.5) !important;
          font-family: 'JetBrains Mono', monospace;
          text-transform: uppercase;
          font-size: 11px;
          letter-spacing: 0.05em;
        }
        .cyberpunk-table .ant-table-tbody > tr > td {
          border-bottom: 1px solid rgba(51, 65, 85, 0.3) !important;
          color: #e2e8f0 !important;
        }
        .cyberpunk-table .ant-table-tbody > tr:hover > td {
          background: rgba(0, 243, 255, 0.05) !important;
        }
        .cyberpunk-table .ant-table-row-selected > td {
          background: rgba(0, 243, 255, 0.1) !important;
        }
        .cyberpunk-table .ant-checkbox-inner {
          background-color: transparent;
          border-color: #475569;
        }
        .cyberpunk-table .ant-checkbox-checked .ant-checkbox-inner {
          background-color: #00f3ff;
          border-color: #00f3ff;
        }
        .cyberpunk-table .ant-tag {
           border: none;
           font-weight: 600;
        }
      `}</style>
    </motion.div>
  );
};

