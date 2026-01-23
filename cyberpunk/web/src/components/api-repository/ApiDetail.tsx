import React, { useState } from 'react';
import { Card, Tag, Button, Tabs, Drawer, Typography, Table, Space, Tooltip, Empty } from 'antd';
import { Copy, Bot, Sparkles, Check } from 'lucide-react';
import type { ApiEndpoint, ApiSchema, ApiParameter } from './types';

const { Paragraph, Text, Title } = Typography;

interface ApiDetailProps {
  endpoint: ApiEndpoint;
}

const MethodTag: React.FC<{ method: string }> = ({ method }) => {
  const colors: Record<string, string> = {
    GET: 'blue',
    POST: 'green',
    PUT: 'orange',
    DELETE: 'red',
    PATCH: 'cyan',
  };
  return <Tag color={colors[method] || 'default'}>{method}</Tag>;
};

const SchemaViewer: React.FC<{ schema?: ApiSchema }> = ({ schema }) => {
  if (!schema) return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="未定义 schema" />;

  return (
    <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 font-mono text-sm">
      <div className="mb-2 text-slate-500">类型: <span className="text-blue-600 font-semibold">{schema.type}</span></div>
      {schema.properties && (
        <div className="space-y-2">
          {Object.entries(schema.properties).map(([key, prop]) => (
            <div key={key} className="pl-4 border-l-2 border-slate-200">
              <div className="flex items-center gap-2">
                <span className="text-purple-700 font-medium">{key}</span>
                <span className="text-slate-500 text-xs">{prop.type}</span>
                {schema.required?.includes(key) && <span className="text-red-500 text-xs">*必填</span>}
              </div>
              {prop.description && <div className="text-slate-500 text-xs mt-1">{prop.description}</div>}
              {prop.example !== undefined && <div className="text-slate-400 text-xs mt-0.5">示例: {String(prop.example)}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export const ApiDetail: React.FC<ApiDetailProps> = ({ endpoint }) => {
  const [aiDrawerOpen, setAiDrawerOpen] = useState(false);
  const [aiContext, setAiContext] = useState<string>('');
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(endpoint.path);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const openAiDrawer = (context: string) => {
    setAiContext(context);
    setAiDrawerOpen(true);
  };

  const paramColumns = [
    {
      title: '名称', dataIndex: 'name', key: 'name', render: (text: string, record: ApiParameter) => (
        <Space>
          <Text strong>{text}</Text>
          {record.required && <Text type="danger">*</Text>}
        </Space>
      )
    },
    { title: '位置', dataIndex: 'in', key: 'in', render: (text: string) => <Tag>{text}</Tag> },
    { title: '类型', dataIndex: 'type', key: 'type', render: (text: string) => <Text code>{text}</Text> },
    { title: '描述', dataIndex: 'description', key: 'description' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-lg shadow-sm">
        <div className="flex items-center gap-4">
          <MethodTag method={endpoint.method} />
          <Title level={4} style={{ margin: 0 }} className="font-mono text-slate-800">{endpoint.path}</Title>
          <Tooltip title={copied ? "已复制!" : "复制路径"}>
            <Button
              type="text"
              icon={copied ? <Check size={16} className="text-green-500" /> : <Copy size={16} />}
              onClick={handleCopy}
              className="text-slate-400 hover:text-slate-600"
            />
          </Tooltip>
        </div>
        <div className="text-slate-400 text-sm">
          最后更新: {endpoint.lastUpdated}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Summary & Description */}
        <Card title="概览" extra={
          <Button
            size="small"
            icon={<Sparkles size={14} />}
            className="text-primary border-primary hover:bg-blue-50"
            onClick={() => openAiDrawer('Overview')}
          >
            Ask AI
          </Button>
        }>
          <Paragraph className="text-lg text-slate-700">{endpoint.summary}</Paragraph>
          {endpoint.description && <Paragraph type="secondary">{endpoint.description}</Paragraph>}
        </Card>

        {/* Parameters */}
        {(endpoint.parameters && endpoint.parameters.length > 0) && (
          <Card title="参数" extra={
            <Button
              size="small"
              icon={<Sparkles size={14} />}
              className="text-primary border-primary hover:bg-blue-50"
              onClick={() => openAiDrawer('Parameters')}
            >
              Ask AI
            </Button>
          }>
            <Table
              dataSource={endpoint.parameters}
              columns={paramColumns}
              pagination={false}
              size="small"
              rowKey="name"
            />
          </Card>
        )}

        {/* Request Body */}
        {endpoint.requestBody && (
          <Card title="请求体" extra={
            <Button
              size="small"
              icon={<Sparkles size={14} />}
              className="text-primary border-primary hover:bg-blue-50"
              onClick={() => openAiDrawer('Request Body')}
            >
              Ask AI
            </Button>
          }>
            <SchemaViewer schema={endpoint.requestBody} />
          </Card>
        )}

        {/* Responses */}
        {endpoint.responses && (
          <Card title="响应" extra={
            <Button
              size="small"
              icon={<Sparkles size={14} />}
              className="text-primary border-primary hover:bg-blue-50"
              onClick={() => openAiDrawer('Responses')}
            >
              Ask AI
            </Button>
          }>
            <Tabs
              type="card"
              items={endpoint.responses.map(resp => ({
                key: String(resp.status),
                label: (
                  <span>
                    <Tag color={resp.status < 300 ? 'success' : resp.status < 400 ? 'warning' : 'error'}>
                      {resp.status}
                    </Tag>
                    {resp.description}
                  </span>
                ),
                children: <SchemaViewer schema={resp.schema} />
              }))}
            />
          </Card>
        )}
      </div>

      <Drawer
        title={
          <div className="flex items-center gap-2 text-primary">
            <Bot size={20} />
            <span>AI 助手</span>
          </div>
        }
        placement="right"
        onClose={() => setAiDrawerOpen(false)}
        open={aiDrawerOpen}
        width={400}
      >
        <div className="space-y-4">
          <div className="p-4 bg-blue-50 border border-blue-100 rounded-lg">
            <Text strong className="text-blue-700">上下文: {aiContext}</Text>
          </div>

          <div className="space-y-4">
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <Bot size={16} className="text-primary" />
              </div>
              <div className="bg-slate-50 p-3 rounded-lg rounded-tl-none border border-slate-200">
                <Paragraph className="mb-0 text-slate-600">
                  我正在为这个端点分析 {aiContext.toLowerCase()}。
                  <br /><br />
                  根据 schema，这个 API 似乎遵循标准的 RESTful 规范。
                  您需要我生成客户端 SDK 代码片段还是解释具体参数？
                </Paragraph>
              </div>
            </div>

            <div className="flex gap-3 flex-row-reverse">
              <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0">
                <div className="w-2 h-2 bg-slate-500 rounded-full" />
              </div>
              <div className="bg-blue-500 p-3 rounded-lg rounded-tr-none text-white">
                <Paragraph className="mb-0 text-white">
                  我应该如何处理响应中的验证错误？
                </Paragraph>
              </div>
            </div>
          </div>

          <div className="absolute bottom-0 left-0 w-full p-4 border-t border-slate-200 bg-white">
            <Button type="primary" block icon={<Sparkles size={16} />}>
              询问 RAG 智能体
            </Button>
          </div>
        </div>
      </Drawer>
    </div>
  );
};
