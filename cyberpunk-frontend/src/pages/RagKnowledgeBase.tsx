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
    filename: '系统架构.pdf',
    type: 'pdf',
    size: '2.4 MB',
    status: 'ready',
    chunks: 156,
    createdAt: '2025-01-10 14:30',
  },
  {
    id: '2',
    filename: 'api文档.md',
    type: 'md',
    size: '45 KB',
    status: 'ready',
    chunks: 42,
    createdAt: '2025-01-12 09:15',
  },
  {
    id: '3',
    filename: '遗留代码库扫描.pdf',
    type: 'pdf',
    size: '15.8 MB',
    status: 'indexing',
    chunks: 0,
    createdAt: '2025-01-14 10:05',
  },
  {
    id: '4',
    filename: 'ui-mockups_v2.png',
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
      message.success(`${rcFile.name} uploaded successfully`);
    }, 1000);
  };

  const handleDelete = (id: string) => {
    setDocuments(prev => prev.filter(doc => doc.id !== id));
    message.success('Document deleted');
  };

  const handleReindex = (id: string) => {
    setDocuments(prev => prev.map(doc => 
      doc.id === id ? { ...doc, status: 'indexing' } : doc
    ));
    message.info('Re-indexing started');
    
    // Simulate re-indexing completion
    setTimeout(() => {
      setDocuments(prev => prev.map(doc => 
        doc.id === id ? { ...doc, status: 'ready', chunks: Math.floor(Math.random() * 100) + 10 } : doc
      ));
      message.success('Indexing completed');
    }, 3000);
  };

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'ready':
        return <Tag color="success" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/20">Ready</Tag>;
      case 'indexing':
        return <Tag color="processing" className="bg-blue-500/10 text-blue-400 border-blue-500/20">Indexing</Tag>;
      case 'error':
        return <Tag color="error" className="bg-red-500/10 text-red-400 border-red-500/20">Error</Tag>;
      default:
        return <Tag>Unknown</Tag>;
    }
  };

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf':
        return <FileText size={18} className="text-red-400" />;
      case 'md':
        return <FileCode size={18} className="text-blue-400" />;
      case 'image':
        return <FileImage size={18} className="text-purple-400" />;
      default:
        return <FileText size={18} className="text-slate-400" />;
    }
  };

  const columns = [
    {
      title: 'Filename',
      dataIndex: 'filename',
      key: 'filename',
      render: (text: string, record: KnowledgeDocument) => (
        <Space>
          {getFileIcon(record.type)}
          <span className="text-slate-200 font-medium">{text}</span>
        </Space>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (text: string) => <span className="uppercase text-xs font-mono text-slate-400">{text}</span>,
    },
    {
      title: 'Size',
      dataIndex: 'size',
      key: 'size',
      render: (text: string) => <span className="text-slate-400 font-mono">{text}</span>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusTag(status),
    },
    {
      title: 'Created At',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (text: string) => <span className="text-slate-500 text-sm">{text}</span>,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: unknown, record: KnowledgeDocument) => (
        <Space size="small">
          <Button 
            type="text" 
            size="small" 
            icon={<RefreshCw size={14} />} 
            className="text-slate-400 hover:text-blue-400"
            onClick={() => handleReindex(record.id)}
            title="Re-index"
            disabled={record.status === 'indexing'}
          />
          <Button 
            type="text" 
            size="small" 
            icon={<Eye size={14} />} 
            className="text-slate-400 hover:text-neon-cyan"
            title="Preview"
          />
          <Popconfirm title="Delete this document?" onConfirm={() => handleDelete(record.id)}>
            <Button 
              type="text" 
              size="small" 
              icon={<Trash2 size={14} />} 
              className="text-slate-400 hover:text-red-400"
              title="Delete"
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100">RAG Knowledge Base</h1>
        <p className="text-slate-400">Manage documents and indexing for retrieval-augmented generation</p>
      </div>

      {/* Stats Row */}
      <Row gutter={16}>
        <Col span={8}>
          <Card variant="borderless" className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50">
            <Statistic 
              title={<span className="text-slate-400 flex items-center gap-2"><Database size={16}/> Total Documents</span>}
              value={totalDocuments} 
              styles={{ content: { color: '#fff' } }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card variant="borderless" className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50">
            <Statistic 
              title={<span className="text-slate-400 flex items-center gap-2"><Layers size={16}/> Total Chunks</span>}
              value={totalChunks} 
              styles={{ content: { color: '#818cf8' } }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card variant="borderless" className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50">
            <Statistic 
              title={<span className="text-slate-400 flex items-center gap-2"><Activity size={16}/> Indexing Status</span>}
              value={indexingCount > 0 ? 'Indexing...' : errorCount > 0 ? 'Has Errors' : 'All Ready'} 
              styles={{ content: { color: indexingCount > 0 ? '#60a5fa' : errorCount > 0 ? '#f87171' : '#34d399', fontSize: '1.5rem' } }}
              suffix={<span className="text-sm text-slate-500 ml-2">({readyCount} ready)</span>}
            />
          </Card>
        </Col>
      </Row>

      {/* Upload Area */}
      <Card 
        variant="borderless" 
        className="bg-slate-800/30 backdrop-blur-sm border border-slate-700/30"
        styles={{ body: { padding: '24px' } }}
      >
        <Dragger 
          customRequest={handleUpload} 
          multiple 
          showUploadList={false}
          className="cyberpunk-dragger"
          style={{ background: 'rgba(15, 23, 42, 0.5)', border: '1px dashed #334155' }}
        >
          <p className="ant-upload-drag-icon">
            <Inbox className="text-neon-cyan mx-auto" size={48} />
          </p>
          <p className="text-slate-300 text-lg mb-2">Click or drag files to this area to upload</p>
          <p className="text-slate-500">
            Support for PDF, Markdown, and Image files. Large files will be automatically chunked.
          </p>
        </Dragger>
      </Card>

      {/* File List */}
      <Card 
        variant="borderless" 
        className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50"
        styles={{ body: { padding: '0' } }}
      >
        <Table
          columns={columns}
          dataSource={documents}
          rowKey="id"
          pagination={{ pageSize: 10 }}
          className="cyberpunk-table"
        />
      </Card>
    </div>
  );
};

