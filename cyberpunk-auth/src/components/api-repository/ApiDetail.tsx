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
  if (!schema) return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No schema defined" />;

  return (
    <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50 font-mono text-sm">
      <div className="mb-2 text-slate-400">Type: <span className="text-indigo-400">{schema.type}</span></div>
      {schema.properties && (
        <div className="space-y-2">
          {Object.entries(schema.properties).map(([key, prop]) => (
            <div key={key} className="pl-4 border-l-2 border-slate-700">
              <div className="flex items-center gap-2">
                <span className="text-cyan-400">{key}</span>
                <span className="text-slate-500 text-xs">{prop.type}</span>
                {schema.required?.includes(key) && <span className="text-red-400 text-xs">*required</span>}
              </div>
              {prop.description && <div className="text-slate-400 text-xs mt-1">{prop.description}</div>}
              {prop.example !== undefined && <div className="text-slate-500 text-xs mt-0.5">Example: {String(prop.example)}</div>}
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
    { title: 'Name', dataIndex: 'name', key: 'name', render: (text: string, record: ApiParameter) => (
      <Space>
        <Text strong>{text}</Text>
        {record.required && <Text type="danger">*</Text>}
      </Space>
    )},
    { title: 'In', dataIndex: 'in', key: 'in', render: (text: string) => <Tag>{text}</Tag> },
    { title: 'Type', dataIndex: 'type', key: 'type', render: (text: string) => <Text code>{text}</Text> },
    { title: 'Description', dataIndex: 'description', key: 'description' },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-lg">
        <div className="flex items-center gap-4">
          <MethodTag method={endpoint.method} />
          <Title level={4} style={{ margin: 0 }} className="font-mono">{endpoint.path}</Title>
          <Tooltip title={copied ? "Copied!" : "Copy Path"}>
            <Button 
              type="text" 
              icon={copied ? <Check size={16} className="text-green-500" /> : <Copy size={16} />} 
              onClick={handleCopy}
            />
          </Tooltip>
        </div>
        <div className="text-slate-400 text-sm">
          Last updated: {endpoint.lastUpdated}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Summary & Description */}
        <Card variant="borderless" className="bg-slate-800/30 border border-slate-700/30">
          <div className="flex justify-between items-start mb-4">
            <Title level={5} style={{ margin: 0 }}>Overview</Title>
            <Button 
              size="small" 
              icon={<Sparkles size={14} />} 
              className="text-indigo-400 border-indigo-500/30 hover:bg-indigo-500/10"
              onClick={() => openAiDrawer('Overview')}
            >
              Ask AI
            </Button>
          </div>
          <Paragraph className="text-lg">{endpoint.summary}</Paragraph>
          {endpoint.description && <Paragraph type="secondary">{endpoint.description}</Paragraph>}
        </Card>

        {/* Parameters */}
        {(endpoint.parameters && endpoint.parameters.length > 0) && (
          <Card variant="borderless" className="bg-slate-800/30 border border-slate-700/30">
             <div className="flex justify-between items-center mb-4">
              <Title level={5} style={{ margin: 0 }}>Parameters</Title>
              <Button 
                size="small" 
                icon={<Sparkles size={14} />} 
                className="text-indigo-400 border-indigo-500/30 hover:bg-indigo-500/10"
                onClick={() => openAiDrawer('Parameters')}
              >
                Ask AI
              </Button>
            </div>
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
          <Card variant="borderless" className="bg-slate-800/30 border border-slate-700/30">
            <div className="flex justify-between items-center mb-4">
              <Title level={5} style={{ margin: 0 }}>Request Body</Title>
              <Button 
                size="small" 
                icon={<Sparkles size={14} />} 
                className="text-indigo-400 border-indigo-500/30 hover:bg-indigo-500/10"
                onClick={() => openAiDrawer('Request Body')}
              >
                Ask AI
              </Button>
            </div>
            <SchemaViewer schema={endpoint.requestBody} />
          </Card>
        )}

        {/* Responses */}
        {endpoint.responses && (
          <Card variant="borderless" className="bg-slate-800/30 border border-slate-700/30">
             <div className="flex justify-between items-center mb-4">
              <Title level={5} style={{ margin: 0 }}>Responses</Title>
              <Button 
                size="small" 
                icon={<Sparkles size={14} />} 
                className="text-indigo-400 border-indigo-500/30 hover:bg-indigo-500/10"
                onClick={() => openAiDrawer('Responses')}
              >
                Ask AI
              </Button>
            </div>
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
          <div className="flex items-center gap-2 text-indigo-400">
            <Bot size={20} />
            <span>AI Assistant</span>
          </div>
        }
        placement="right"
        onClose={() => setAiDrawerOpen(false)}
        open={aiDrawerOpen}
        width={400}
        className="bg-slate-900/95 backdrop-blur-md"
      >
        <div className="space-y-4">
          <div className="p-4 bg-indigo-500/10 border border-indigo-500/20 rounded-lg">
            <Text strong className="text-indigo-300">Context: {aiContext}</Text>
          </div>
          
          <div className="space-y-4">
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center flex-shrink-0">
                <Bot size={16} className="text-indigo-400" />
              </div>
              <div className="bg-slate-800 p-3 rounded-lg rounded-tl-none border border-slate-700">
                <Paragraph className="mb-0 text-slate-300">
                  I'm analyzing the {aiContext.toLowerCase()} for this endpoint. 
                  <br/><br/>
                  Based on the schema, this API appears to follow standard RESTful conventions. 
                  Would you like me to generate a client SDK snippet or explain specific parameters?
                </Paragraph>
              </div>
            </div>
            
             <div className="flex gap-3 flex-row-reverse">
              <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center flex-shrink-0">
                <div className="w-2 h-2 bg-slate-400 rounded-full" />
              </div>
              <div className="bg-indigo-600/20 p-3 rounded-lg rounded-tr-none border border-indigo-500/30">
                <Paragraph className="mb-0 text-slate-300">
                  How should I handle the validation errors in the response?
                </Paragraph>
              </div>
            </div>
          </div>
          
          <div className="absolute bottom-0 left-0 w-full p-4 border-t border-slate-700 bg-slate-900/50 backdrop-blur">
             <Button type="primary" block icon={<Sparkles size={16}/>}>
               Ask RAG Agent
             </Button>
          </div>
        </div>
      </Drawer>
    </div>
  );
};
