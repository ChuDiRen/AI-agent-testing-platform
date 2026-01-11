"""
AnythingChatRAG - 多模态知识检索引擎

支持6种检索模式：
1. local - 本地实体和关系检索
2. global - 全局知识图谱探索
3. hybrid - 混合检索策略
4. naive - 向量相似性搜索
5. mix - 综合检索（推荐）
6. bypass - 直接查询
"""
import asyncio
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json
from datetime import datetime
import hashlib
import re

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
# from langchain.vectorstores import Chroma
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.document_loaders import (
#     PyPDFLoader, 
#     Docx2txtLoader, 
#     UnstructuredExcelLoader,
#     UnstructuredMarkdownLoader
# )
# from langchain.schema import Document


class RAGQuery(BaseModel):
    """RAG查询参数"""
    query: str = Field(description="查询文本")
    mode: str = Field(default="mix", description="检索模式")
    top_k: int = Field(default=10, description="返回结果数量")
    chunk_top_k: int = Field(default=5, description="文本块数量")
    enable_rerank: bool = Field(default=True, description="启用重排序")


class RAGResult(BaseModel):
    """RAG检索结果"""
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="实体信息")
    relationships: List[Dict[str, Any]] = Field(default_factory=list, description="关系信息")
    text_chunks: List[Dict[str, Any]] = Field(default_factory=list, description="文本块")
    references: List[Dict[str, Any]] = Field(default_factory=list, description="引用信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class AnythingChatRAG:
    """AnythingChatRAG多模态知识检索引擎"""
    
    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = workspace_dir or Path("./rag_workspace")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化向量数据库
        self.vectorstore = None
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            base_url="https://api.siliconflow.cn/v1",
            api_key="YOUR_SILICONFLOW_API_KEY"
        )
        
        # 初始化LLM - 使用硅基流动
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.3,
            base_url="https://api.siliconflow.cn/v1",
            api_key="YOUR_SILICONFLOW_API_KEY"
        )
        
        # 初始化文档处理器
        self.document_processors = {
            'pdf': lambda x: [],  # PyPDFLoader,
            'docx': lambda x: [],  # Docx2txtLoader,
            'xlsx': lambda x: [],  # UnstructuredExcelLoader,
            'md': lambda x: [],  # UnstructuredMarkdownLoader,
            'txt': lambda x: []  # lambda x: [Document(page_content=x, metadata={})]
        }
        
        # 初始化知识图谱
        self.knowledge_graph = {}
        self.entity_index = {}
        self.relationship_index = {}
        
        # 初始化检索模式
        self.retrieval_modes = {
            'local': self._local_retrieval,
            'global': self._global_retrieval,
            'hybrid': self._hybrid_retrieval,
            'naive': self._naive_retrieval,
            'mix': self._mix_retrieval,
            'bypass': self._bypass_retrieval
        }
    
    async def aquery(self, query: str, mode: str = "mix", **kwargs) -> RAGResult:
        """异步RAG查询"""
        rag_query = RAGQuery(
            query=query,
            mode=mode,
            top_k=kwargs.get('top_k', 10),
            chunk_top_k=kwargs.get('chunk_top_k', 5),
            enable_rerank=kwargs.get('enable_rerank', True)
        )
        
        # 根据模式选择检索方法
        if mode in self.retrieval_modes:
            result = await self.retrieval_modes[mode](rag_query)
        else:
            result = await self._mix_retrieval(rag_query)
        
        return result
    
    async def _local_retrieval(self, query: RAGQuery) -> RAGResult:
        """本地实体和关系检索"""
        print(f"🔍 Local retrieval: {query.query}")
        
        # 实体提取
        entities = await self._extract_entities(query.query)
        
        # 关系检索
        relationships = await self._extract_relationships(query.query, entities)
        
        # 本地文档检索
        local_chunks = await self._search_local_documents(query.query, query.top_k)
        
        return RAGResult(
            entities=entities,
            relationships=relationships,
            text_chunks=local_chunks,
            references=[],
            metadata={"mode": "local", "timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _global_retrieval(self, query: RAGQuery) -> RAGResult:
        """全局知识图谱探索"""
        print(f"🌐 Global retrieval: {query.query}")
        
        # 全局知识图谱查询
        global_entities = await self._query_knowledge_graph(query.query)
        
        # 全局关系探索
        global_relationships = await self._explore_global_relationships(query.query)
        
        # 全局文档检索
        global_chunks = await self._search_global_documents(query.query, query.top_k)
        
        return RAGResult(
            entities=global_entities,
            relationships=global_relationships,
            text_chunks=global_chunks,
            references=[],
            metadata={"mode": "global", "timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _hybrid_retrieval(self, query: RAGQuery) -> RAGResult:
        """混合检索策略"""
        print(f"🔄 Hybrid retrieval: {query.query}")
        
        # 并行执行本地和全局检索
        local_task = self._local_retrieval(query)
        global_task = self._global_retrieval(query)
        
        local_result, global_result = await asyncio.gather(local_task, global_task)
        
        # 合并结果
        merged_entities = local_result.entities + global_result.entities
        merged_relationships = local_result.relationships + global_result.relationships
        merged_chunks = local_result.text_chunks + global_result.text_chunks
        
        return RAGResult(
            entities=merged_entities,
            relationships=merged_relationships,
            text_chunks=merged_chunks,
            references=[],
            metadata={"mode": "hybrid", "timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _naive_retrieval(self, query: RAGQuery) -> RAGResult:
        """向量相似性搜索"""
        print(f"🧠 Naive retrieval: {query.query}")
        
        if not self.vectorstore:
            await self._initialize_vectorstore()
        
        # 向量相似性搜索
        similar_docs = await self.vectorstore.asimilarity_search(
            query.query, 
            k=query.top_k
        )
        
        text_chunks = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "similarity": 1.0 - getattr(doc, 'score', 0.0)
            }
            for doc in similar_docs
        ]
        
        return RAGResult(
            entities=[],
            relationships=[],
            text_chunks=text_chunks,
            references=[],
            metadata={"mode": "naive", "timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _mix_retrieval(self, query: RAGQuery) -> RAGResult:
        """综合检索（推荐）"""
        print(f"🎯 Mix retrieval: {query.query}")
        
        # 并行执行所有检索模式
        tasks = [
            self._local_retrieval(query),
            self._global_retrieval(query),
            self._naive_retrieval(query)
        ]
        
        local_result, global_result, naive_result = await asyncio.gather(*tasks)
        
        # 智能合并和重排序
        mixed_entities = await self._merge_and_rerank_entities([
            local_result.entities,
            global_result.entities
        ])
        
        mixed_relationships = await self._merge_and_rerank_relationships([
            local_result.relationships,
            global_result.relationships
        ])
        
        mixed_chunks = await self._merge_and_rerank_chunks([
            local_result.text_chunks,
            global_result.text_chunks,
            naive_result.text_chunks
        ])
        
        return RAGResult(
            entities=mixed_entities,
            relationships=mixed_relationships,
            text_chunks=mixed_chunks,
            references=[],
            metadata={"mode": "mix", "timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _bypass_retrieval(self, query: RAGQuery) -> RAGResult:
        """直接查询"""
        print(f"⚡ Bypass retrieval: {query.query}")
        
        # 直接LLM查询
        direct_response = await self.llm.ainvoke(query.query)
        
        text_chunks = [
            {
                "content": direct_response.content,
                "metadata": {"source": "direct_llm"},
                "similarity": 1.0
            }
        ]
        
        return RAGResult(
            entities=[],
            relationships=[],
            text_chunks=text_chunks,
            references=[],
            metadata={"mode": "bypass", "timestamp": datetime.utcnow().isoformat()}
        )
    
    async def _extract_entities(self, query: str) -> List[Dict[str, Any]]:
        """提取实体"""
        # 使用LLM提取API相关的实体
        prompt = f"""
        从以下查询中提取API相关的实体信息：
        查询：{query}
        
        请提取以下类型的实体：
        1. API接口名称
        2. HTTP方法（GET, POST, PUT, DELETE等）
        3. 参数名称
        4. 认证方式
        5. 响应字段
        
        返回JSON格式：
        {{
            "entities": [
                {{
                    "type": "api_endpoint",
                    "name": "接口名称",
                    "description": "描述",
                    "confidence": 0.9
                }}
            ]
        }}
        """
        
        response = await self.llm.ainvoke(prompt)
        
        try:
            # 解析JSON响应
            import json
            data = json.loads(response.content)
            return data.get("entities", [])
        except:
            return []
    
    async def _extract_relationships(self, query: str, entities: List[Dict]) -> List[Dict[str, Any]]:
        """提取关系"""
        # 基于实体提取关系
        relationships = []
        
        for entity in entities:
            if entity.get("type") == "api_endpoint":
                # API依赖关系
                relationships.append({
                    "source": entity.get("name"),
                    "target": "authentication",
                    "relationship_type": "requires",
                    "confidence": 0.8
                })
        
        return relationships
    
    async def _search_local_documents(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """搜索本地文档"""
        # 模拟本地文档搜索
        local_docs = [
            {
                "content": f"API接口文档：{query}的详细说明",
                "metadata": {"source": "local_api_docs", "type": "api_spec"},
                "similarity": 0.9
            },
            {
                "content": f"测试用例：{query}相关的测试场景",
                "metadata": {"source": "local_test_cases", "type": "test_case"},
                "similarity": 0.8
            }
        ]
        
        return local_docs[:top_k]
    
    async def _query_knowledge_graph(self, query: str) -> List[Dict[str, Any]]:
        """查询知识图谱"""
        # 模拟知识图谱查询
        kg_entities = [
            {
                "type": "api_module",
                "name": "user_management",
                "description": "用户管理模块",
                "confidence": 0.95
            },
            {
                "type": "api_endpoint",
                "name": "/api/users",
                "description": "用户列表接口",
                "confidence": 0.9
            }
        ]
        
        return kg_entities
    
    async def _explore_global_relationships(self, query: str) -> List[Dict[str, Any]]:
        """探索全局关系"""
        global_relationships = [
            {
                "source": "user_management",
                "target": "authentication",
                "relationship_type": "depends_on",
                "confidence": 0.85
            },
            {
                "source": "/api/users",
                "target": "jwt_token",
                "relationship_type": "requires",
                "confidence": 0.9
            }
        ]
        
        return global_relationships
    
    async def _search_global_documents(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """搜索全局文档"""
        global_docs = [
            {
                "content": f"全局API规范：{query}的完整文档",
                "metadata": {"source": "global_api_specs", "type": "api_doc"},
                "similarity": 0.92
            }
        ]
        
        return global_docs[:top_k]
    
    async def _initialize_vectorstore(self):
        """初始化向量数据库"""
        # 创建向量存储
        self.vectorstore = Chroma(
            collection_name="api_knowledge",
            embedding_function=self.embeddings,
            persist_directory=str(self.workspace_dir / "vectorstore")
        )
    
    async def _merge_and_rerank_entities(self, entity_lists: List[List[Dict]]) -> List[Dict[str, Any]]:
        """合并和重排序实体"""
        merged = []
        seen_entities = set()
        
        for entity_list in entity_lists:
            for entity in entity_list:
                entity_key = f"{entity.get('type', '')}:{entity.get('name', '')}"
                if entity_key not in seen_entities:
                    merged.append(entity)
                    seen_entities.add(entity_key)
        
        # 按置信度排序
        merged.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        return merged[:10]
    
    async def _merge_and_rerank_relationships(self, relationship_lists: List[List[Dict]]) -> List[Dict[str, Any]]:
        """合并和重排序关系"""
        merged = []
        seen_relationships = set()
        
        for relationship_list in relationship_lists:
            for rel in relationship_list:
                rel_key = f"{rel.get('source', '')}:{rel.get('target', '')}:{rel.get('relationship_type', '')}"
                if rel_key not in seen_relationships:
                    merged.append(rel)
                    seen_relationships.add(rel_key)
        
        # 按置信度排序
        merged.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        return merged[:10]
    
    async def _merge_and_rerank_chunks(self, chunk_lists: List[List[Dict]]) -> List[Dict[str, Any]]:
        """合并和重排序文本块"""
        merged = []
        seen_chunks = set()
        
        for chunk_list in chunk_lists:
            for chunk in chunk_list:
                chunk_key = hashlib.md5(chunk.get('content', '').encode()).hexdigest()
                if chunk_key not in seen_chunks:
                    merged.append(chunk)
                    seen_chunks.add(chunk_key)
        
        # 按相似度排序
        merged.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        return merged[:10]
