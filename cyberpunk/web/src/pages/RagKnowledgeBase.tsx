import React, { useState } from 'react';
import { Card, Upload, Table, Button, Tag, Space, Statistic, message, Row, Col, Popconfirm } from 'antd';
import {
  Inbox,
  FileText,
  Trash2,
  RefreshCw,
  Eye,
  Database,
  Layers,
  Activity,
  FileCode,
  FileImage
} from 'lucide-react';
import type { UploadProps } from 'antd';
import type { RcFile } from 'antd/es/upload';

interface KnowledgeDocument {
  id: string;
  filename: string;
  type: 'pdf' | 'md' | 'image' | 'other';
  size: string;
  status: 'indexing' | 'ready' | 'error';
  chunks: number;
  createdAt: string;
}

const MOCK_DOCUMENTS: KnowledgeDocument[] = [
  {
    id: '1',
    filename: '系统架构说明书.pdf',
    type: 'pdf',
    size: '2.4 MB',
    status: 'ready',
    chunks: 156,
    createdAt: '2025-01-10 14:30',
  },
  {
    id: '2',
    filename: 'API 接口文档.md',
    type: 'md',
    size: '45 KB',
    status: 'ready',
    chunks: 42,
    createdAt: '2025-01-12 09:15',
  },
  {
    id: '3',
    filename: '旧版代码扫描报告.pdf',
    type: 'pdf',
    size: '15.8 MB',
    status: 'indexing',
    chunks: 0,
    createdAt: '2025-01-14 10:05',
  },
  {
    id: '4',
    filename: 'UI 交互原型 v2.png',
    type: 'image',
    size: '3.2 MB',
    status: 'error',
    chunks: 0,
    createdAt: '2025-01-13 16:45',
  },
];

const { Dragger } = Upload;

export const RagKnowledgeBase: React.FC = () => {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>(MOCK_DOCUMENTS);

  // Calculate Stats
  const totalDocuments = documents.length;
  const totalChunks = documents.reduce((acc, doc) => acc + doc.chunks, 0);
  const indexingCount = documents.filter(doc => doc.status === 'indexing').length;
  const errorCount = documents.filter(doc => doc.status === 'error').length;
  const readyCount = documents.filter(doc => doc.status === 'ready').length;

  const handleUpload: UploadProps['customRequest'] = ({ file, onSuccess }) => {
    setTimeout(() => {
      const rcFile = file as RcFile;
      const type: KnowledgeDocument['type'] = rcFile.name.endsWith('.pdf') ? 'pdf'
        : rcFile.name.endsWith('.md') ? 'md'
          : rcFile.name.match(/\.(jpg|jpeg|png|gif)$/) ? 'image'
            : 'other';

      const newDoc: KnowledgeDocument = {
        id: Date.now().toString(),
        filename: rcFile.name,
        type: type,
        size: `${(rcFile.size / 1024 / 1024).toFixed(2)} MB`,
        status: 'indexing',
        chunks: 0,
        createdAt: new Date().toLocaleString(),
      };

      setDocuments(prev => [newDoc, ...prev]);
      if (onSuccess) onSuccess("ok");
      message.success(`${rcFile.name} 上传成功`);
    }, 1000);
  };

  const handleDelete = (id: string) => {
    setDocuments(prev => prev.filter(doc => doc.id !== id));
    message.success('文档已删除');
  };

  const handleReindex = (id: string) => {
    setDocuments(prev => prev.map(doc =>
      doc.id === id ? { ...doc, status: 'indexing' } : doc
    ));
    message.info('开始重新索引');

    // Simulate re-indexing completion
    setTimeout(() => {
      setDocuments(prev => prev.map(doc =>
        doc.id === id ? { ...doc, status: 'ready', chunks: Math.floor(Math.random() * 100) + 10 } : doc
      ));
      message.success('索引已完成');
    }, 3000);
  };

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'ready':
        return <Tag color="success" className="bg-emerald-50 text-emerald-600 border-emerald-200">就绪</Tag>;
      case 'indexing':
        return <Tag color="processing" className="bg-blue-50 text-blue-600 border-blue-200">索引中</Tag>;
      case 'error':
        return <Tag color="error" className="bg-red-50 text-red-600 border-red-200">错误</Tag>;
      default:
        return <Tag>未知</Tag>;
    }
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf':
        return <FileText size={18} className="text-red-500" />;
      case 'md':
        return <FileCode size={18} className="text-blue-500" />;
      case 'image':
        return <FileImage size={18} className="text-purple-500" />;
      default:
        return <FileText size={18} className="text-slate-400" />;
    }
  };

  const columns = [
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
      render: (text: string, record: KnowledgeDocument) => (
        <Space>
          {getFileIcon(record.type)}
          <span className="text-slate-700 font-medium">{text}</span>
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (text: string) => <span className="uppercase text-xs font-mono text-slate-500">{text}</span>,
    },
    {
      title: '大小',
      dataIndex: 'size',
      key: 'size',
      render: (text: string) => <span className="text-slate-500 font-mono">{text}</span>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (text: string) => <span className="text-slate-500 text-sm">{text}</span>,
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: unknown, record: KnowledgeDocument) => (
        <Space size="small">
          <Button
            type="text"
            size="small"
            icon={<RefreshCw size={14} />}
            className="text-slate-400 hover:text-blue-600"
            onClick={() => handleReindex(record.id)}
            title="重新索引"
            disabled={record.status === 'indexing'}
          />
          <Button
            type="text"
            size="small"
            icon={<Eye size={14} />}
            className="text-slate-400 hover:text-primary"
            title="预览"
          />
          <Popconfirm title="确定要删除此文档吗？" onConfirm={() => handleDelete(record.id)} okText="确定" cancelText="取消">
            <Button
              type="text"
              size="small"
              icon={<Trash2 size={14} />}
              className="text-slate-400 hover:text-red-500"
              title="删除"
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="space-y-6 p-6 max-w-6xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">RAG 知识库</h1>
        <p className="text-slate-500">管理用于检索增强生成的文档和索引</p>
      </div>

      {/* Stats Row */}
      <Row gutter={16}>
        <Col span={8}>
          <Card bordered={false} className="shadow-sm">
            <Statistic
              title={<span className="text-slate-500 flex items-center gap-2"><Database size={16} /> 文档总数</span>}
              value={totalDocuments}
              valueStyle={{ color: '#1e293b' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card bordered={false} className="shadow-sm">
            <Statistic
              title={<span className="text-slate-500 flex items-center gap-2"><Layers size={16} /> 总切片数</span>}
              value={totalChunks}
              valueStyle={{ color: '#2563EB' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card bordered={false} className="shadow-sm">
            <Statistic
              title={<span className="text-slate-500 flex items-center gap-2"><Activity size={16} /> 索引状态</span>}
              value={indexingCount > 0 ? '索引中...' : errorCount > 0 ? '存在错误' : '全部就绪'}
              valueStyle={{ color: indexingCount > 0 ? '#3b82f6' : errorCount > 0 ? '#ef4444' : '#10b981', fontSize: '1.5rem' }}
              suffix={<span className="text-sm text-slate-400 ml-2">({readyCount} 就绪)</span>}
            />
          </Card>
        </Col>
      </Row>

      {/* Upload Area */}
      <Card
        bordered={false}
        className="shadow-sm"
        styles={{ body: { padding: '24px' } }}
      >
        <Dragger
          customRequest={handleUpload}
          multiple
          showUploadList={false}
          style={{ background: '#F8FAFC', border: '1px dashed #E2E8F0' }}
        >
          <p className="ant-upload-drag-icon">
            <Inbox className="text-blue-500 mx-auto" size={48} />
          </p>
          <p className="text-slate-700 text-lg mb-2 font-medium">点击或拖拽文件到此区域上传</p>
          <p className="text-slate-500">
            支持 PDF, Markdown 和图片文件。大文件将自动进行切片处理。
          </p>
        </Dragger>
      </Card>

      {/* File List */}
      <Card
        bordered={false}
        className="shadow-sm overflow-hidden"
        styles={{ body: { padding: '0' } }}
      >
        <Table
          columns={columns}
          dataSource={documents}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
};
