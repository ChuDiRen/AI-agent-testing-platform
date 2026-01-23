import React, { useState, useRef } from 'react';
import { Button, Input, Drawer, Tag, Typography, Space, Badge, Tooltip } from 'antd';
import {
  Search,
  ZoomIn,
  ZoomOut,
  Maximize,
  Share2,
  FileText,
  Database,
  Server,
  Key,
  Globe,
  Cpu
} from 'lucide-react';

const { Text, Paragraph } = Typography;

// --- Types ---
interface GraphNode {
  id: string;
  label: string;
  type: 'service' | 'database' | 'endpoint' | 'concept' | 'infrastructure';
  x: number;
  y: number;
  description: string;
  documents: { title: string; snippet: string; score: number }[];
}

interface GraphEdge {
  source: string;
  target: string;
  label?: string;
}

// --- Mock Data ---
// --- Mock Data ---
const MOCK_NODES: GraphNode[] = [
  {
    id: 'auth-service',
    label: '认证服务 (Auth)',
    type: 'service',
    x: 400,
    y: 300,
    description: '负责用户认证和会话管理的核心微服务。',
    documents: [
      { title: '系统架构 v2.0', snippet: '认证服务处理所有登录请求...', score: 0.95 },
      { title: 'API 规范', snippet: 'POST /auth/login 返回 JWT 令牌...', score: 0.88 }
    ]
  },
  {
    id: 'user-db',
    label: '用户数据库',
    type: 'database',
    x: 400,
    y: 500,
    description: '存储用户凭据和个人资料信息的 PostgreSQL 数据库。',
    documents: [
      { title: '数据库 Schema', snippet: '表 `users` 包含哈希密码...', score: 0.92 }
    ]
  },
  {
    id: 'jwt',
    label: 'JWT 令牌',
    type: 'concept',
    x: 600,
    y: 300,
    description: '用于无状态认证的 JSON Web 令牌。',
    documents: [
      { title: '安全协议', snippet: '我们使用 RS256 签名 JWT 令牌...', score: 0.85 }
    ]
  },
  {
    id: 'login-api',
    label: '/api/login',
    type: 'endpoint',
    x: 200,
    y: 300,
    description: '用户登录的公共端点。',
    documents: [
      { title: 'API 文档', snippet: '速率限制为每分钟 5 次请求...', score: 0.98 }
    ]
  },
  {
    id: 'rate-limiter',
    label: '速率限制器',
    type: 'infrastructure',
    x: 200,
    y: 150,
    description: '基于 Redis 的速率限制中间件。',
    documents: [
      { title: '基础设施设置', snippet: '用于速率限制的 Redis 集群配置...', score: 0.76 }
    ]
  },
  {
    id: 'payment-gw',
    label: '支付网关',
    type: 'service',
    x: 600,
    y: 150,
    description: '外部支付网关集成。',
    documents: []
  },
];

const MOCK_EDGES: GraphEdge[] = [
  { source: 'login-api', target: 'auth-service', label: '调用' },
  { source: 'auth-service', target: 'user-db', label: '查询' },
  { source: 'auth-service', target: 'jwt', label: '签发' },
  { source: 'login-api', target: 'rate-limiter', label: '检查' },
  { source: 'auth-service', target: 'payment-gw', label: '通知' },
];

// --- Components ---

const NodeIcon = ({ type, size = 20 }: { type: string; size?: number }) => {
  switch (type) {
    case 'service': return <Server size={size} className="text-blue-600" />;
    case 'database': return <Database size={size} className="text-emerald-500" />;
    case 'endpoint': return <Globe size={size} className="text-sky-500" />;
    case 'infrastructure': return <Cpu size={size} className="text-orange-500" />;
    case 'concept': return <Key size={size} className="text-purple-500" />;
    default: return <FileText size={size} className="text-slate-400" />;
  }
};

export const KnowledgeGraphExplorer: React.FC = () => {
  const [nodes] = useState(MOCK_NODES);
  const [edges] = useState(MOCK_EDGES);
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [searchQuery, setSearchQuery] = useState('');

  const containerRef = useRef<HTMLDivElement>(null);

  // --- Graph Interaction Handlers ---

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const scaleAmount = -e.deltaY * 0.001;
    const newScale = Math.max(0.1, Math.min(4, transform.k * (1 + scaleAmount)));

    // Zoom towards center (simplified)
    setTransform(prev => ({ ...prev, k: newScale }));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).tagName !== 'circle' && (e.target as HTMLElement).tagName !== 'text') {
      setIsDragging(true);
      setDragStart({ x: e.clientX - transform.x, y: e.clientY - transform.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setTransform(prev => ({
        ...prev,
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      }));
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleZoomIn = () => setTransform(prev => ({ ...prev, k: Math.min(4, prev.k * 1.2) }));
  const handleZoomOut = () => setTransform(prev => ({ ...prev, k: Math.max(0.1, prev.k / 1.2) }));
  const handleFitView = () => setTransform({ x: 0, y: 0, k: 1 });

  const handleNodeClick = (e: React.MouseEvent, node: GraphNode) => {
    e.stopPropagation();
    setSelectedNode(node);
  };

  // --- Filtering ---
  const filteredNodes = nodes.map(n => ({
    ...n,
    dimmed: searchQuery && !n.label.toLowerCase().includes(searchQuery.toLowerCase())
  }));

  return (
    <div className="relative w-full h-[calc(100vh-64px)] overflow-hidden bg-slate-50 text-slate-800">

      {/* Background Grid */}
      <div className="absolute inset-0 opacity-10 pointer-events-none"
        style={{
          backgroundImage: 'radial-gradient(#94a3b8 1px, transparent 1px)',
          backgroundSize: '30px 30px'
        }}
      />

      {/* Graph Area */}
      <div
        ref={containerRef}
        className="w-full h-full cursor-grab active:cursor-grabbing"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <svg className="w-full h-full pointer-events-none">
          <g transform={`translate(${transform.x},${transform.y}) scale(${transform.k})`}>

            {/* Edges */}
            {edges.map((edge, i) => {
              const src = nodes.find(n => n.id === edge.source);
              const tgt = nodes.find(n => n.id === edge.target);
              if (!src || !tgt) return null;

              return (
                <g key={i}>
                  <line
                    x1={src.x} y1={src.y}
                    x2={tgt.x} y2={tgt.y}
                    stroke="#cbd5e1"
                    strokeWidth="2"
                    className="transition-colors duration-300"
                  />
                  {edge.label && (
                    <text
                      x={(src.x + tgt.x) / 2}
                      y={(src.y + tgt.y) / 2}
                      fill="#64748b"
                      fontSize="10"
                      textAnchor="middle"
                      dy={-5}
                      className="bg-slate-50 font-medium"
                    >
                      {edge.label}
                    </text>
                  )}
                </g>
              );
            })}

            {/* Nodes */}
            {filteredNodes.map(node => (
              <g
                key={node.id}
                transform={`translate(${node.x},${node.y})`}
                className={`pointer-events-auto cursor-pointer transition-opacity duration-300 ${node.dimmed ? 'opacity-30' : 'opacity-100'}`}
                onClick={(e) => handleNodeClick(e, node)}
              >
                {/* Glow Effect for Selected */}
                {selectedNode?.id === node.id && (
                  <circle r="35" fill="none" stroke="#3b82f6" strokeWidth="2" className="animate-pulse" />
                )}

                {/* Node Circle */}
                <circle
                  r="25"
                  fill="#ffffff"
                  stroke={
                    node.type === 'service' ? '#2563EB' :
                      node.type === 'database' ? '#10B981' :
                        node.type === 'endpoint' ? '#0EA5E9' : '#64748B'
                  }
                  strokeWidth="2"
                  className="transition-colors hover:fill-slate-50 shadow-sm"
                />

                {/* Icon inside Node */}
                <foreignObject x="-10" y="-10" width="20" height="20" className="pointer-events-none">
                  <div className="flex items-center justify-center w-full h-full">
                    <NodeIcon type={node.type} size={16} />
                  </div>
                </foreignObject>

                {/* Label */}
                <text
                  y="45"
                  fill="#1e293b"
                  fontSize="12"
                  textAnchor="middle"
                  className="font-medium pointer-events-none select-none drop-shadow-sm"
                >
                  {node.label}
                </text>
              </g>
            ))}
          </g>
        </svg>
      </div>

      {/* Floating Control Panel */}
      <div className="absolute bottom-6 right-6 flex flex-col gap-2 bg-white/90 backdrop-blur-md p-2 rounded-lg border border-slate-200 shadow-xl">
        <Tooltip title="适配视图" placement="left">
          <Button type="text" icon={<Maximize size={18} />} onClick={handleFitView} className="text-slate-600 hover:text-primary hover:bg-slate-50" />
        </Tooltip>
        <Tooltip title="放大" placement="left">
          <Button type="text" icon={<ZoomIn size={18} />} onClick={handleZoomIn} className="text-slate-600 hover:text-primary hover:bg-slate-50" />
        </Tooltip>
        <Tooltip title="缩小" placement="left">
          <Button type="text" icon={<ZoomOut size={18} />} onClick={handleZoomOut} className="text-slate-600 hover:text-primary hover:bg-slate-50" />
        </Tooltip>
      </div>

      {/* Search Bar */}
      <div className="absolute top-6 left-6 w-80">
        <Input
          prefix={<Search size={16} className="text-slate-400" />}
          placeholder="搜索节点..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="bg-white/90 backdrop-blur-md border-slate-200 shadow-sm text-slate-800 focus:border-primary hover:border-slate-300 h-10 rounded-lg"
          allowClear
        />
      </div>

      {/* Legend */}
      <div className="absolute top-6 right-6 bg-white/90 backdrop-blur-md p-4 rounded-xl border border-slate-200 shadow-lg pointer-events-none">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">图例</h3>
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <span className="w-2 h-2 rounded-full bg-blue-600"></span> 服务
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span> 数据库
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-600">
            <span className="w-2 h-2 rounded-full bg-sky-500"></span> 端点
          </div>
        </div>
      </div>

      {/* Detail Drawer */}
      <Drawer
        title={
          <div className="flex items-center gap-2">
            <NodeIcon type={selectedNode?.type || ''} />
            <span className="text-slate-800">{selectedNode?.label}</span>
          </div>
        }
        placement="right"
        onClose={() => setSelectedNode(null)}
        open={!!selectedNode}
        width={400}
        mask={false}
        className="shadow-2xl"
      >
        {selectedNode && (
          <div className="space-y-6">

            {/* Basic Info */}
            <div>
              <Tag color="blue" className="mb-2 uppercase text-[10px] font-bold tracking-wider">{selectedNode.type}</Tag>
              <Paragraph className="text-slate-600 mt-2">
                {selectedNode.description}
              </Paragraph>
            </div>

            {/* Metrics/Stats (Mock) */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                <div className="text-xs text-slate-500 mb-1">连接数</div>
                <div className="text-xl font-mono text-blue-600 font-semibold">
                  {edges.filter(e => e.source === selectedNode.id || e.target === selectedNode.id).length}
                </div>
              </div>
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-100">
                <div className="text-xs text-slate-500 mb-1">文档数</div>
                <div className="text-xl font-mono text-emerald-600 font-semibold">
                  {selectedNode.documents.length}
                </div>
              </div>
            </div>

            {/* Associated Documents */}
            <div>
              <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Share2 size={14} /> 知识片段
              </h4>
              <div className="space-y-3">
                {selectedNode.documents.length > 0 ? selectedNode.documents.map((doc, idx) => (
                  <div key={idx} className="bg-white p-3 rounded-lg border border-slate-200 hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer group">
                    <div className="flex justify-between items-start mb-1">
                      <Text className="text-slate-800 font-medium text-sm group-hover:text-primary">{doc.title}</Text>
                      <Badge count={`${(doc.score * 100).toFixed(0)}%`} color={doc.score > 0.9 ? '#10b981' : '#f59e0b'} />
                    </div>
                    <Text className="text-slate-500 text-xs line-clamp-2">
                      {doc.snippet}
                    </Text>
                  </div>
                )) : (
                  <div className="text-slate-400 text-sm italic p-4 text-center border border-dashed border-slate-200 rounded">
                    未找到相关文档。
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="pt-4 border-t border-slate-100">
              <Space>
                <Button type="primary">编辑节点</Button>
                <Button>展开邻居</Button>
              </Space>
            </div>

          </div>
        )}
      </Drawer>
    </div>
  );
};
