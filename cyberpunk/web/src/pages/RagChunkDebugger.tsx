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
# 系统架构规范 v2.0

## 1. 简介
本文档概述了次世代认证服务 (NextGen Authentication Service) 的架构蓝图。该系统旨在处理高并发登录请求，同时确保严格的安全合规性。

## 2. 核心组件

### 2.1 认证服务 (Auth Service)
认证服务是所有身份验证请求的网关。它实现了 OAuth2.0 协议并支持 OpenID Connect。
- 职责：
  - 凭据验证
  - 令牌签发 (JWT)
  - 会话管理

### 2.2 用户数据库
我们使用带有主从复制设置的 PostgreSQL 15。
- Schema：
  - users: 存储身份信息
  - roles: RBAC 定义
  - permissions: 细粒度访问控制

### 2.3 缓存层
Redis 集群用于：
- 速率限制计数器 (令牌桶算法)
- 短期会话令牌
- JWT 黑名单 (JTI)

## 3. 安全协议
所有通信必须使用 TLS 1.3 加密。密码使用 Argon2id 进行哈希处理，最小内存成本为 64MB。

## 4. 可扩展性
该服务使用 Docker 进行容器化，并通过 Kubernetes 进行编排。水平 Pod 自动扩缩容 (HPA) 根据 CPU 和请求数指标进行配置。
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
    content: "# 系统架构规范 v2.0\n\n## 1. 简介\n本文档概述了次世代认证服务 (NextGen Authentication Service) 的架构蓝图。",
    page: 1,
    charStart: 0,
    charEnd: 145
  },
  {
    id: 'c2',
    content: "该系统旨在处理高并发登录请求，同时确保严格的安全合规性。\n\n## 2. 核心组件",
    page: 1,
    charStart: 146,
    charEnd: 275
  },
  {
    id: 'c3',
    content: "### 2.1 认证服务 (Auth Service)\n认证服务是所有身份验证请求的网关。它实现了 OAuth2.0 协议并支持 OpenID Connect。\n- 职责：\n  - 凭据验证\n  - 令牌签发 (JWT)\n  - 会话管理",
    page: 1,
    charStart: 276,
    charEnd: 530
  },
  {
    id: 'c4',
    content: "### 2.2 用户数据库\n我们使用带有主从复制设置的 PostgreSQL 15。\n- Schema：\n  - users: 存储身份信息\n  - roles: RBAC 定义\n  - permissions: 细粒度访问控制",
    page: 2,
    charStart: 531,
    charEnd: 740
  },
  {
    id: 'c5',
    content: "### 2.3 缓存层\nRedis 集群用于：\n- 速率限制计数器 (令牌桶算法)\n- 短期会话令牌\n- JWT 黑名单 (JTI)",
    page: 2,
    charStart: 741,
    charEnd: 900
  },
  {
    id: 'c6',
    content: "## 3. 安全协议\n所有通信必须使用 TLS 1.3 加密。密码使用 Argon2id 进行哈希处理，最小内存成本为 64MB。",
    page: 3,
    charStart: 901,
    charEnd: 1050
  },
  {
    id: 'c7',
    content: "## 4. 可扩展性\n该服务使用 Docker 进行容器化，并通过 Kubernetes 进行编排。水平 Pod 自动扩缩容 (HPA) 根据 CPU 和请求数指标进行配置。",
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
    <div className="h-[calc(100vh-64px)] flex flex-col p-6 gap-6 overflow-hidden">
      {/* Header */}
      <div className="flex justify-between items-center shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
            <Highlighter className="text-blue-600" />
            RAG 切片调试器
          </h1>
          <p className="text-slate-500">检查切片策略并模拟检索相关性</p>
        </div>
        <div className="flex gap-2">
          <Tag className="bg-slate-100 text-slate-600 border-slate-200 px-3 py-1">
            <FileText size={12} className="inline mr-2" />
            系统架构-v2.pdf
          </Tag>
          <Tag className="bg-slate-100 text-slate-600 border-slate-200 px-3 py-1">
            <Hash size={12} className="inline mr-2" />
            {MOCK_CHUNKS.length} 个切片
          </Tag>
        </div>
      </div>

      <div className="flex-1 flex gap-6 min-h-0">

        {/* Left Pane: Original Document Preview */}
        <Card
          title={<span className="text-slate-800 font-semibold flex items-center gap-2"><AlignLeft size={16} /> 原始文档</span>}
          className="w-1/2 h-full flex flex-col shadow-sm"
          styles={{ body: { flex: 1, overflow: 'hidden', padding: 0 } }}
        >
          <div className="h-full overflow-y-auto p-6 bg-slate-50 font-mono text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">
            {MOCK_ORIGINAL_DOC}
          </div>
        </Card>

        {/* Right Pane: Chunk List */}
        <div className="w-1/2 flex flex-col gap-4 min-h-0">

          {/* Search Bar */}
          <div className="shrink-0">
            <Input
              prefix={<Search size={16} className="text-slate-400" />}
              placeholder="输入查询以测试检索评分 (例如: 'redis 缓存', 'oauth')..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-12 text-lg shadow-sm"
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
                      ? 'bg-blue-50 border-blue-400 shadow-md transform -translate-y-0.5'
                      : 'bg-white border-slate-200 hover:border-blue-300 hover:shadow-sm'
                    }
                  `}
                >
                  {/* Relevance Score Badge (Only visible when searching) */}
                  {searchQuery && (
                    <div className="absolute top-4 right-4">
                      <Badge
                        count={`评分: ${(chunk.score * 100).toFixed(1)}%`}
                        style={{
                          backgroundColor: isHighRelevance ? '#10b981' : chunk.score > 0.4 ? '#f59e0b' : '#94a3b8',
                          color: '#fff',
                          boxShadow: 'none'
                        }}
                      />
                    </div>
                  )}

                  {/* Metadata Header */}
                  <div className="flex items-center gap-3 mb-3 text-xs text-slate-400 font-mono uppercase tracking-wider">
                    <span className="flex items-center gap-1">
                      <FileText size={12} /> 第 {chunk.page} 页
                    </span>
                    <span className="w-1 h-1 rounded-full bg-slate-300" />
                    <span className="flex items-center gap-1">
                      <Maximize2 size={12} /> {chunk.content.length} 字符
                    </span>
                    <span className="w-1 h-1 rounded-full bg-slate-300" />
                    <span>ID: {chunk.id}</span>
                  </div>

                  {/* Chunk Content */}
                  <div className={`font-mono text-sm leading-relaxed p-3 rounded border transition-colors ${isSelected
                    ? 'bg-blue-100/50 text-slate-700 border-blue-200'
                    : 'bg-slate-50 text-slate-600 border-slate-100 group-hover:bg-white group-hover:border-slate-200'
                    }`}>
                    {chunk.content}
                  </div>

                  {/* Footer (Embedding ID) */}
                  <div className="mt-3 flex justify-between items-center">
                    <Text className="text-[10px] text-slate-400 font-mono">
                      vector_id: {chunk.embeddingId || `vec_${chunk.id}_${Date.now().toString().slice(-6)}`}
                    </Text>
                    {isSelected && (
                      <Button type="link" size="small" className="text-blue-600 p-0 h-auto flex items-center gap-1">
                        检查向量 <ChevronRight size={12} />
                      </Button>
                    )}
                  </div>
                </div>
              );
            })}

            {scoredChunks.length === 0 && (
              <Empty description={<span className="text-slate-500">未找到切片</span>} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
