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
import { Card } from '../components/ui/Card';

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
    name: '验证合法凭证登录',
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
    name: '检查 SQL 注入漏洞',
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
    name: '创建发票校验',
    tag: 'Functional',
    api: '/invoices',
    method: 'POST',
    status: 'Failed',
    creator: 'Morpheus',
    lastRun: '2024-03-14 15:45',
    codeSnippet: `test('应该校验发票金额', async () => {
  const response = await client.post('/invoices', {
    amount: -100, // 无效
    currency: 'USD'
  });
  expect(response.status).toBe(400);
  expect(response.data.error).toBe('Invalid amount');
});`
  },
  {
    id: 'TC-004',
    name: '获取用户资料性能测试',
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
  // 设置过期令牌
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
    message.success(`已对 ${selectedRowKeys.length} 个项目执行 ${action}`);
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

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'Passed': return '已通过';
      case 'Failed': return '已失败';
      case 'Pending': return '等候中';
      case 'Skipped': return '已跳过';
      default: return status;
    }
  };

  const getTagLabel = (tag: string) => {
    switch (tag) {
      case 'Functional': return '功能测试';
      case 'Security': return '安全测试';
      case 'Performance': return '性能测试';
      case 'Integration': return '集成测试';
      default: return tag;
    }
  };

  const columns: ColumnsType<TestCase> = [
    {
      title: '用例 ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
      render: (text) => <span className="font-mono text-slate-500">{text}</span>,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text) => <span className="font-medium text-slate-900">{text}</span>,
    },
    {
      title: '标签',
      dataIndex: 'tag',
      key: 'tag',
      width: 120,
      render: (tag) => {
        let color = 'default';
        if (tag === 'Functional') color = 'blue';
        if (tag === 'Security') color = 'purple';
        if (tag === 'Performance') color = 'orange';
        return <Tag color={color} className="border-none">{getTagLabel(tag)}</Tag>;
      }
    },
    {
      title: '关联 API',
      key: 'api',
      width: 250,
      render: (_, record) => (
        <Space size="small">
          <Tag className={`
            font-mono font-bold border-none 
            ${record.method === 'GET' ? 'text-blue-600 bg-blue-50' :
              record.method === 'POST' ? 'text-green-600 bg-green-50' :
                record.method === 'DELETE' ? 'text-red-600 bg-red-50' :
                  'text-orange-600 bg-orange-50'}
          `}>
            {record.method}
          </Tag>
          <span className="font-mono text-xs text-slate-500">{record.api}</span>
        </Space>
      ),
    },
    {
      title: '最近状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => (
        <Space size={4} className={`
          ${status === 'Passed' ? 'text-green-600' :
            status === 'Failed' ? 'text-red-600' :
              status === 'Pending' ? 'text-yellow-600' : 'text-slate-500'}
        `}>
          {getStatusIcon(status)}
          <span>{getStatusLabel(status)}</span>
        </Space>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 80,
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
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">用例管理</h1>
          <p className="text-slate-500 text-sm mt-1">管理、组织并执行您的测试套件</p>
        </div>
        <div className="flex gap-3">
          <Button icon={<Play size={16} />} className="hover:border-primary hover:text-primary">
            运行套件
          </Button>
          <Button type="primary" icon={<Plus size={16} />} className="bg-primary hover:bg-blue-700">
            新建用例
          </Button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="p-4 bg-white border border-slate-200 rounded-lg flex flex-wrap gap-4 items-center shadow-sm">
        <Input
          prefix={<Search size={14} className="text-slate-400" />}
          placeholder="搜索用例..."
          className="w-64"
          value={searchText}
          onChange={e => setSearchText(e.target.value)}
        />

        <Select
          placeholder="状态"
          allowClear
          className="w-32"
          onChange={setFilterStatus}
          options={[
            { value: 'Passed', label: '已通过' },
            { value: 'Failed', label: '已失败' },
            { value: 'Pending', label: '等待中' },
            { value: 'Skipped', label: '已跳过' },
          ]}
        />

        <Select
          placeholder="标签"
          allowClear
          className="w-32"
          onChange={setFilterTag}
          options={[
            { value: 'Functional', label: '功能测试' },
            { value: 'Security', label: '安全测试' },
            { value: 'Performance', label: '性能测试' },
            { value: 'Integration', label: '集成测试' },
          ]}
        />
      </div>

      {/* Batch Actions */}
      {selectedRowKeys.length > 0 && (
        <div className="flex items-center gap-4 p-3 bg-blue-50 border border-blue-100 rounded-lg text-blue-700">
          <span className="font-medium">已选择 {selectedRowKeys.length} 项</span>
          <div className="h-4 w-px bg-blue-200" />
          <Button
            size="small"
            type="text"
            className="text-blue-700 hover:text-blue-800 hover:bg-blue-100 font-medium"
            onClick={() => handleBatchAction('添加到套件')}
          >
            添加到套件
          </Button>
          <Button
            size="small"
            type="text"
            danger
            icon={<Trash2 size={14} />}
            onClick={() => handleBatchAction('删除')}
          >
            删除
          </Button>
        </div>
      )}

      {/* Table */}
      <Card className="overflow-hidden">
        <Table
          rowSelection={rowSelection}
          columns={columns}
          dataSource={filteredData}
          rowKey="id"
          expandable={{
            expandedRowRender: (record) => (
              <div className="p-4 bg-slate-50 border-t border-slate-100">
                <div className="flex items-center gap-2 mb-2 text-primary text-xs uppercase tracking-wider font-semibold">
                  <FileCode size={12} />
                  测试实现 (代码)
                </div>
                <div className="rounded-md overflow-hidden border border-slate-200 shadow-sm">
                  <SyntaxHighlighter
                    language="javascript"
                    style={vscDarkPlus as unknown as Record<string, React.CSSProperties>}
                    customStyle={{ margin: 0, background: '#1e293b', padding: '1rem' }}
                    showLineNumbers={true}
                  >
                    {record.codeSnippet}
                  </SyntaxHighlighter>
                </div>
                <div className="mt-4 flex gap-4 text-xs text-slate-500 font-medium">
                  <span className="flex items-center gap-1">
                    <User size={12} /> 创建者 {record.creator}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar size={12} /> 最近运行: {record.lastRun}
                  </span>
                </div>
              </div>
            ),
            expandIcon: ({ expanded, onExpand, record }) => (
              <Button
                type="text"
                size="small"
                onClick={e => onExpand(record, e)}
                className="text-slate-400 hover:text-primary transition-colors"
              >
                {expanded ? '隐藏' : '代码'}
              </Button>
            ),
            columnTitle: '代码'
          }}
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
};
