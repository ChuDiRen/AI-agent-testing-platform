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
      title: 'Method',
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
          <Tag color={color} className="font-mono font-bold border-none bg-opacity-20">
            {method}
          </Tag>
        );
      },
    },
    {
      title: 'Path',
      dataIndex: 'path',
      key: 'path',
      render: (path: string) => (
        <span className="font-mono text-slate-300">{path}</span>
      ),
    },
    {
      title: 'Summary',
      dataIndex: 'summary',
      key: 'summary',
      render: (text: string) => (
        <span className="text-slate-400">{text}</span>
      ),
    },
    {
      title: 'Last Updated',
      dataIndex: 'lastUpdated',
      key: 'lastUpdated',
      width: 150,
      render: (date: string) => (
        <span className="flex items-center gap-2 text-slate-500 text-xs">
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
        className="cyberpunk-table"
        rowClassName="hover:bg-slate-800/30 transition-colors"
      />
      <style>{`
        .cyberpunk-table .ant-table {
          background: transparent !important;
        }
        .cyberpunk-table .ant-table-thead > tr > th {
          background: rgba(15, 23, 42, 0.5) !important;
          color: #94a3b8 !important;
          border-bottom: 1px solid rgba(51, 65, 85, 0.5) !important;
        }
        .cyberpunk-table .ant-table-tbody > tr > td {
          border-bottom: 1px solid rgba(51, 65, 85, 0.3) !important;
        }
        .cyberpunk-table .ant-table-tbody > tr:hover > td {
          background: rgba(30, 41, 59, 0.5) !important;
        }
      `}</style>
    </div>
  );
};
