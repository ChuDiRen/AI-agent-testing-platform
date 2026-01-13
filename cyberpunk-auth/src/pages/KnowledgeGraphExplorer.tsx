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
const MOCK_NODES: GraphNode[] = [
  { 
    id: 'auth-service', 
    label: '认证服务', 
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
    description: 'PostgreSQL 数据库存储用户凭据和配置文件信息。',
    documents: [
      { title: 'Database Schema', snippet: 'Table `users` contains hashed passwords...', score: 0.92 }
    ]
  },
  { 
    id: 'jwt', 
    label: 'JWT 令牌', 
    type: 'concept', 
    x: 600, 
    y: 300,
    description: 'JSON Web Token used for stateless authentication.',
    documents: [
      { title: 'Security Protocols', snippet: 'We use RS256 for signing JWT tokens...', score: 0.85 }
    ]
  },
  { 
    id: 'login-api', 
    label: '/api/login', 
    type: 'endpoint', 
    x: 200, 
    y: 300,
    description: 'Public endpoint for user login.',
    documents: [
      { title: 'API Documentation', snippet: 'Rate limited to 5 requests per minute...', score: 0.98 }
    ]
  },
  { 
    id: 'rate-limiter', 
    label: 'Rate Limiter', 
    type: 'infrastructure', 
    x: 200, 
    y: 150,
    description: 'Redis-based rate limiting middleware.',
    documents: [
      { title: 'Infrastructure Setup', snippet: 'Redis cluster configuration for rate limiting...', score: 0.76 }
    ]
  },
  { 
    id: 'payment-gw', 
    label: 'Payment GW', 
    type: 'service', 
    x: 600, 
    y: 150,
    description: 'External payment gateway integration.',
    documents: []
  },
];

const MOCK_EDGES: GraphEdge[] = [
  { source: 'login-api', target: 'auth-service', label: 'calls' },
  { source: 'auth-service', target: 'user-db', label: 'queries' },
  { source: 'auth-service', target: 'jwt', label: 'issues' },
  { source: 'login-api', target: 'rate-limiter', label: 'checked by' },
  { source: 'auth-service', target: 'payment-gw', label: 'notifies' },
];

// --- Components ---

const NodeIcon = ({ type, size = 20 }: { type: string; size?: number }) => {
  switch (type) {
    case 'service': return <Server size={size} className="text-indigo-400" />;
    case 'database': return <Database size={size} className="text-emerald-400" />;
    case 'endpoint': return <Globe size={size} className="text-blue-400" />;
    case 'infrastructure': return <Cpu size={size} className="text-orange-400" />;
    case 'concept': return <Key size={size} className="text-purple-400" />;
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
    <div className="relative w-full h-[calc(100vh-64px)] overflow-hidden bg-[#0a0a0f] text-slate-200">
      
      {/* Background Grid */}
      <div className="absolute inset-0 opacity-10 pointer-events-none" 
           style={{ 
             backgroundImage: 'radial-gradient(#4f46e5 1px, transparent 1px)', 
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
                    stroke="#334155" 
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
                      className="bg-slate-900"
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
                className={`pointer-events-auto cursor-pointer transition-opacity duration-300 ${node.dimmed ? 'opacity-20' : 'opacity-100'}`}
                onClick={(e) => handleNodeClick(e, node)}
              >
                {/* Glow Effect for Selected */}
                {selectedNode?.id === node.id && (
                  <circle r="35" fill="none" stroke="#6366f1" strokeWidth="2" className="animate-pulse" />
                )}
                
                {/* Node Circle */}
                <circle 
                  r="25" 
                  fill="#1e293b" 
                  stroke={
                    node.type === 'service' ? '#818cf8' : 
                    node.type === 'database' ? '#34d399' : 
                    node.type === 'endpoint' ? '#60a5fa' : '#94a3b8'
                  } 
                  strokeWidth="2" 
                  className="transition-colors hover:fill-slate-800"
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
                  fill="#cbd5e1" 
                  fontSize="12" 
                  textAnchor="middle" 
                  className="font-mono font-bold pointer-events-none select-none shadow-black drop-shadow-md"
                >
                  {node.label}
                </text>
              </g>
            ))}
          </g>
        </svg>
      </div>

      {/* Floating Control Panel */}
      <div className="absolute bottom-6 right-6 flex flex-col gap-3 bg-slate-900/80 backdrop-blur-md p-3 rounded-xl border border-slate-700/50 shadow-2xl">
        <Tooltip title="Fit View" placement="left">
          <Button type="text" icon={<Maximize size={18} />} onClick={handleFitView} className="text-slate-300 hover:text-white hover:bg-slate-800" />
        </Tooltip>
        <Tooltip title="Zoom In" placement="left">
          <Button type="text" icon={<ZoomIn size={18} />} onClick={handleZoomIn} className="text-slate-300 hover:text-white hover:bg-slate-800" />
        </Tooltip>
        <Tooltip title="Zoom Out" placement="left">
          <Button type="text" icon={<ZoomOut size={18} />} onClick={handleZoomOut} className="text-slate-300 hover:text-white hover:bg-slate-800" />
        </Tooltip>
      </div>

      {/* Search Bar */}
      <div className="absolute top-6 left-6 w-80">
        <Input 
          prefix={<Search size={16} className="text-slate-500" />} 
          placeholder="Search nodes..." 
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="bg-slate-900/80 backdrop-blur-md border-slate-700/50 text-slate-200 focus:border-indigo-500 hover:border-slate-600 h-10 rounded-lg"
          allowClear
        />
      </div>

      {/* Legend */}
      <div className="absolute top-6 right-6 bg-slate-900/80 backdrop-blur-md p-4 rounded-xl border border-slate-700/50 shadow-lg pointer-events-none">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Legend</h3>
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs text-slate-300">
            <span className="w-2 h-2 rounded-full bg-indigo-400"></span> Service
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span> Database
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-300">
            <span className="w-2 h-2 rounded-full bg-blue-400"></span> Endpoint
          </div>
        </div>
      </div>

      {/* Detail Drawer */}
      <Drawer
        title={
          <div className="flex items-center gap-2">
            <NodeIcon type={selectedNode?.type || ''} />
            <span className="text-slate-100">{selectedNode?.label}</span>
          </div>
        }
        placement="right"
        onClose={() => setSelectedNode(null)}
        open={!!selectedNode}
        width={400}
        mask={false}
        className="cyberpunk-drawer"
        styles={{ 
          body: { padding: 0, background: '#0f172a' },
          header: { background: '#1e293b', borderBottom: '1px solid #334155', color: '#fff' }
        }}
      >
        {selectedNode && (
          <div className="p-6 space-y-6">
            
            {/* Basic Info */}
            <div>
              <Tag color="geekblue" className="mb-2 uppercase text-[10px] font-bold tracking-wider">{selectedNode.type}</Tag>
              <Paragraph className="text-slate-300 mt-2">
                {selectedNode.description}
              </Paragraph>
            </div>

            {/* Metrics/Stats (Mock) */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-800/50 p-3 rounded border border-slate-700/50">
                <div className="text-xs text-slate-500 mb-1">Connections</div>
                <div className="text-xl font-mono text-indigo-400">
                  {edges.filter(e => e.source === selectedNode.id || e.target === selectedNode.id).length}
                </div>
              </div>
              <div className="bg-slate-800/50 p-3 rounded border border-slate-700/50">
                <div className="text-xs text-slate-500 mb-1">Docs</div>
                <div className="text-xl font-mono text-emerald-400">
                  {selectedNode.documents.length}
                </div>
              </div>
            </div>

            {/* Associated Documents */}
            <div>
              <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Share2 size={14} /> Knowledge Fragments
              </h4>
              <div className="space-y-3">
                {selectedNode.documents.length > 0 ? selectedNode.documents.map((doc, idx) => (
                  <div key={idx} className="bg-slate-800/30 p-3 rounded border border-slate-700/50 hover:border-indigo-500/50 transition-colors cursor-pointer group">
                    <div className="flex justify-between items-start mb-1">
                      <Text className="text-indigo-300 font-medium text-sm group-hover:text-indigo-200">{doc.title}</Text>
                      <Badge count={`${(doc.score * 100).toFixed(0)}%`} color={doc.score > 0.9 ? '#10b981' : '#f59e0b'} />
                    </div>
                    <Text className="text-slate-400 text-xs line-clamp-2">
                      {doc.snippet}
                    </Text>
                  </div>
                )) : (
                  <div className="text-slate-500 text-sm italic p-4 text-center border border-dashed border-slate-800 rounded">
                    No linked documents found.
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="pt-4 border-t border-slate-800">
              <Space>
                <Button type="primary" className="bg-indigo-600 hover:bg-indigo-500">Edit Node</Button>
                <Button>Expand Neighbors</Button>
              </Space>
            </div>

          </div>
        )}
      </Drawer>
    </div>
  );
};
