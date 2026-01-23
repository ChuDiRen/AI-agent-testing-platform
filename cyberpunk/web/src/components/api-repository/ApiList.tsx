import React from 'react';
import { Table, Tag } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { ApiEndpoint } from './types';
import { Clock } from 'lucide-react';

interface ApiListProps {
  endpoints: ApiEndpoint[];
  loading?: boolean;
}

export const ApiList: React.FC<ApiListProps> = ({ endpoints, loading }) => {
  const columns: ColumnsType<ApiEndpoint> = [
    {
      title: '方法',
      dataIndex: 'method',
      key: 'method',
      width: 100,
      render: (method: string) => {
        let color = 'default';
        if (method === 'GET') color = 'blue';
        if (method === 'POST') color = 'green';
        if (method === 'PUT') color = 'orange';
        if (method === 'DELETE') color = 'red';
        if (method === 'PATCH') color = 'purple';

        return (
          <Tag color={color} className="font-mono font-bold border-none">
            {method}
          </Tag>
        );
      },
    },
    {
      title: '路径',
      dataIndex: 'path',
      key: 'path',
      render: (path: string) => (
        <span className="font-mono text-slate-700 font-medium">{path}</span>
      ),
    },
    {
      title: '摘要',
      dataIndex: 'summary',
      key: 'summary',
      render: (text: string) => (
        <span className="text-slate-500">{text}</span>
      ),
    },
    {
      title: '最后更新',
      dataIndex: 'lastUpdated',
      key: 'lastUpdated',
      width: 150,
      render: (date: string) => (
        <span className="flex items-center gap-2 text-slate-400 text-xs">
          <Clock size={12} />
          {date}
        </span>
      ),
    },
  ];

  return (
    <div className="w-full">
      <Table
        columns={columns}
        dataSource={endpoints}
        rowKey="id"
        pagination={false}
        loading={loading}
        rowClassName="hover:bg-slate-50 transition-colors"
      />
    </div>
  );
};
