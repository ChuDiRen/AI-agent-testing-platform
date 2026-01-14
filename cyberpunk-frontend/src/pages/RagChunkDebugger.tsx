import React, { useState, useMemo } from 'react';
import { Card, Input, Tag, Typography, Badge, Empty, Button } from 'antd';
import { 
  Search, 
  FileText, 
  Hash, 
  AlignLeft, 
  Highlighter,
  ChevronRight,
  Maximize2
} from 'lucide-react';

const { Text } = Typography;

// --- Mock Data ---

const MOCK_ORIGINAL_DOC = `
# System Architecture Specification v2.0

## 1. Introduction
This document outlines the architectural blueprint for the NextGen Authentication Service. The system is designed to handle high-concurrency login requests while ensuring strict security compliance.

## 2. Core Components

### 2.1 Auth Service
The Auth Service is the gateway for all authentication requests. It implements the OAuth2.0 protocol and supports OpenID Connect.
- Responsibilities:
  - Credential verification
  - Token issuance (JWT)
  - Session management

### 2.2 User Database
We utilize PostgreSQL 15 with a master-slave replication setup.
- Schema:
  - users: Stores identity information
  - roles: RBAC definitions
  - permissions: Granular access controls

### 2.3 Caching Layer
Redis Cluster is used for:
- Rate limiting counters (Token Bucket algorithm)
- Short-lived session tokens
- Blacklisted JWTs (JTI)

## 3. Security Protocols
All communication must be encrypted using TLS 1.3. Passwords are hashed using Argon2id with a minimum memory cost of 64MB.

## 4. Scalability
The service is containerized using Docker and orchestrated via Kubernetes. Horizontal Pod Autoscaling (HPA) is configured based on CPU and Request Count metrics.
`;

interface Chunk {
  id: string;
  content: string;
  page: number;
  charStart: number;
  charEnd: number;
  embeddingId?: string;
}

const MOCK_CHUNKS: Chunk[] = [
  {
    id: 'c1',
    content: "# System Architecture Specification v2.0\n\n## 1. Introduction\nThis document outlines the architectural blueprint for the NextGen Authentication Service.",
    page: 1,
    charStart: 0,
    charEnd: 145
  },
  {
    id: 'c2',
    content: "The system is designed to handle high-concurrency login requests while ensuring strict security compliance.\n\n## 2. Core Components",
    page: 1,
    charStart: 146,
    charEnd: 275
  },
  {
    id: 'c3',
    content: "### 2.1 Auth Service\nThe Auth Service is the gateway for all authentication requests. It implements the OAuth2.0 protocol and supports OpenID Connect.\n- Responsibilities:\n  - Credential verification\n  - Token issuance (JWT)\n  - Session management",
    page: 1,
    charStart: 276,
    charEnd: 530
  },
  {
    id: 'c4',
    content: "### 2.2 User Database\nWe utilize PostgreSQL 15 with a master-slave replication setup.\n- Schema:\n  - users: Stores identity information\n  - roles: RBAC definitions\n  - permissions: Granular access controls",
    page: 2,
    charStart: 531,
    charEnd: 740
  },
  {
    id: 'c5',
    content: "### 2.3 Caching Layer\nRedis Cluster is used for:\n- Rate limiting counters (Token Bucket algorithm)\n- Short-lived session tokens\n- Blacklisted JWTs (JTI)",
    page: 2,
    charStart: 741,
    charEnd: 900
  },
  {
    id: 'c6',
    content: "## 3. Security Protocols\nAll communication must be encrypted using TLS 1.3. Passwords are hashed using Argon2id with a minimum memory cost of 64MB.",
    page: 3,
    charStart: 901,
    charEnd: 1050
  },
  {
    id: 'c7',
    content: "## 4. Scalability\nThe service is containerized using Docker and orchestrated via Kubernetes. Horizontal Pod Autoscaling (HPA) is configured based on CPU and Request Count metrics.",
    page: 3,
    charStart: 1051,
    charEnd: 1230
  }
];

export const RagChunkDebugger: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedChunkId, setSelectedChunkId] = useState<string | null>(null);

  // Calculate scores based on search query (Mock simulation)
  const scoredChunks = useMemo(() => {
    if (!searchQuery) return MOCK_CHUNKS.map(c => ({ ...c, score: 0 }));

    return MOCK_CHUNKS.map(chunk => {
      // Simple mock scoring: presence of keywords
      const lowerContent = chunk.content.toLowerCase();
      const lowerQuery = searchQuery.toLowerCase();
      const terms = lowerQuery.split(' ').filter(t => t.trim());
      
      let matches = 0;
      terms.forEach(term => {
        if (lowerContent.includes(term)) matches++;
      });

      // Mock score: matches / total terms * random jitter for realism
      const baseScore = terms.length > 0 ? matches / terms.length : 0;
      // Add slight randomness to simulate vector similarity nuances
      const score = baseScore > 0 ? Math.min(0.99, baseScore * 0.9 + Math.random() * 0.1) : 0;
      
      return { ...chunk, score };
    }).sort((a, b) => b.score - a.score);
  }, [searchQuery]);

  return (
    <div className="h-[calc(100vh-64px)] flex flex-col p-6 gap-6">
      {/* Header */}
      <div className="flex justify-between items-center shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
            <Highlighter className="text-neon-cyan" />
            RAG 块调试器
          </h1>
          <p className="text-slate-400">检查分块策略并模拟检索相关性</p>
        </div>
        <div className="flex gap-2">
          <Tag className="bg-slate-800 text-slate-300 border-slate-700 px-3 py-1">
            <FileText size={12} className="inline mr-2" />
            系统架构-v2.pdf
          </Tag>
          <Tag className="bg-slate-800 text-slate-300 border-slate-700 px-3 py-1">
            <Hash size={12} className="inline mr-2" />
            {MOCK_CHUNKS.length} 个块
          </Tag>
        </div>
      </div>

      <div className="flex-1 flex gap-6 min-h-0">
        
        {/* Left Pane: Original Document Preview */}
        <Card 
          title={<span className="text-slate-300 font-semibold flex items-center gap-2"><AlignLeft size={16}/> 原始文档</span>}
          className="w-1/2 h-full flex flex-col bg-slate-800/50 backdrop-blur-sm border-slate-700/50"
          styles={{ body: { flex: 1, overflow: 'hidden', padding: 0 } }}
        >
          <div className="h-full overflow-y-auto p-6 bg-[#0f172a] font-mono text-sm text-slate-400 leading-relaxed whitespace-pre-wrap">
             {MOCK_ORIGINAL_DOC}
          </div>
        </Card>

        {/* Right Pane: Chunk List */}
        <div className="w-1/2 flex flex-col gap-4 min-h-0">
          
          {/* Search Bar */}
          <div className="shrink-0">
            <Input 
              prefix={<Search size={16} className="text-slate-500" />}
              placeholder="Enter query to test retrieval score (e.g., 'redis caching', 'oauth')..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-900/80 border-slate-700 text-slate-200 h-12 text-lg focus:border-neon-cyan"
              allowClear
            />
          </div>

          {/* Cards Container */}
          <div className="flex-1 overflow-y-auto pr-2 space-y-4">
            {scoredChunks.map((chunk) => {
              const isHighRelevance = chunk.score > 0.7;
              const isSelected = selectedChunkId === chunk.id;
              
              return (
                <div 
                  key={chunk.id}
                  onClick={() => setSelectedChunkId(chunk.id)}
                  className={`
                    group relative p-4 rounded-xl border transition-all cursor-pointer
                    ${isSelected 
                      ? 'bg-indigo-900/20 border-neon-cyan shadow-[0_0_15px_rgba(99,102,241,0.2)]' 
                      : 'bg-slate-800/40 border-slate-700/50 hover:bg-slate-800 hover:border-slate-600'
                    }
                  `}
                >
                  {/* Relevance Score Badge (Only visible when searching) */}
                  {searchQuery && (
                    <div className="absolute top-4 right-4">
                      <Badge 
                        count={`Score: ${(chunk.score * 100).toFixed(1)}%`} 
                        style={{ 
                          backgroundColor: isHighRelevance ? '#10b981' : chunk.score > 0.4 ? '#f59e0b' : '#64748b',
                          color: '#fff',
                          boxShadow: 'none'
                        }} 
                      />
                    </div>
                  )}

                  {/* Metadata Header */}
                  <div className="flex items-center gap-3 mb-3 text-xs text-slate-500 font-mono uppercase tracking-wider">
                    <span className="flex items-center gap-1">
                      <FileText size={12} /> Page {chunk.page}
                    </span>
                    <span className="w-1 h-1 rounded-full bg-slate-700" />
                    <span className="flex items-center gap-1">
                      <Maximize2 size={12} /> {chunk.content.length} chars
                    </span>
                    <span className="w-1 h-1 rounded-full bg-slate-700" />
                    <span>ID: {chunk.id}</span>
                  </div>

                  {/* Chunk Content */}
                  <div className="font-mono text-sm text-slate-300 leading-relaxed bg-slate-950/50 p-3 rounded border border-slate-800/50 group-hover:border-slate-700 transition-colors">
                    {chunk.content}
                  </div>

                  {/* Footer (Embedding ID) */}
                  <div className="mt-3 flex justify-between items-center">
                    <Text className="text-[10px] text-slate-600 font-mono">
                      vector_id: {chunk.embeddingId || `vec_${chunk.id}_${Date.now().toString().slice(-6)}`}
                    </Text>
                    {isSelected && (
                       <Button type="link" size="small" className="text-neon-cyan p-0 h-auto flex items-center gap-1">
                         Inspect Vector <ChevronRight size={12} />
                       </Button>
                    )}
                  </div>
                </div>
              );
            })}
            
            {scoredChunks.length === 0 && (
               <Empty description={<span className="text-slate-500">No chunks found</span>} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

