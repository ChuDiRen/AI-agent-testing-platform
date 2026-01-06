"""
RAG检索智能体 - 知识检索和API文档查询

职责：
- 从知识库检索API接口信息
- 查询API文档和规范
- 提供上下文相关的API知识
- 支持多种检索模式
"""
from typing import Any, Dict, List, Optional
import json
from datetime import datetime

from core.simple_rag import AnythingChatRAGEngine, RetrievalMode
from core.models import RAGEntity, RAGChunk
from core.logging_config import get_logger

logger = get_logger(__name__)


class RAGRetrievalAgent:
    """
    RAG检索智能体
    
    核心功能：
    - 知识库查询
    - API文档检索
    - 上下文增强
    - 多模态检索
    """
    
    def __init__(self, rag_engine: Optional[AnythingChatRAGEngine] = None):
        """
        初始化RAG检索智能体
        
        Args:
            rag_engine: RAG引擎实例（可选）
        """
        self.rag_engine = rag_engine or AnythingChatRAGEngine()
        self.agent_name = "RAG检索Agent"
        logger.info(f"{self.agent_name} 初始化完成")
    
    async def retrieve_api_info(
        self,
        query: str,
        mode: str = "mix",
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        检索API接口信息
        
        Args:
            query: 查询文本
            mode: 检索模式（local/global/hybrid/naive/mix/bypass）
            top_k: 返回的最大结果数
        
        Returns:
            检索结果字典
        """
        logger.info(f"{self.agent_name} 开始检索: query='{query}', mode={mode}")
        
        try:
            # 执行RAG检索
            result = await self.rag_engine.aquery(
                query=query,
                mode=mode,
                top_k=top_k,
                chunk_top_k=5,
                enable_rerank=True
            )
            
            # 构建响应
            response = {
                "success": True,
                "query": query,
                "mode": mode,
                "entities": [
                    {
                        "entity_id": e.entity_id,
                        "entity_name": e.entity_name,
                        "entity_type": e.entity_type,
                        "description": e.description,
                        "properties": e.properties
                    }
                    for e in result.entities
                ],
                "chunks": [
                    {
                        "chunk_id": c.chunk_id,
                        "content": c.content,
                        "source": c.source,
                        "score": c.score
                    }
                    for c in result.chunks
                ],
                "confidence": result.confidence,
                "processing_time": result.processing_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"{self.agent_name} 检索完成: 找到 {len(result.entities)} 个实体")
            return response
            
        except Exception as e:
            logger.error(f"{self.agent_name} 检索失败: {e}", exc_info=e)
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def search_api_documentation(
        self,
        api_name: str,
        doc_type: str = "openapi"
    ) -> Dict[str, Any]:
        """
        搜索API文档
        
        Args:
            api_name: API名称
            doc_type: 文档类型（openapi/swagger/graphql）
        
        Returns:
            文档搜索结果
        """
        logger.info(f"{self.agent_name} 搜索API文档: {api_name}")
        
        # 构建查询
        query = f"{api_name} {doc_type} API documentation"
        
        # 执行检索
        result = await self.retrieve_api_info(query, mode="global", top_k=5)
        
        return {
            "api_name": api_name,
            "doc_type": doc_type,
            "documentation": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_api_context(
        self,
        endpoint: str,
        method: str = "GET"
    ) -> Dict[str, Any]:
        """
        获取API端点的上下文信息
        
        Args:
            endpoint: API端点路径
            method: HTTP方法
        
        Returns:
            上下文信息
        """
        logger.info(f"{self.agent_name} 获取API上下文: {method} {endpoint}")
        
        # 构建查询
        query = f"{method} {endpoint} API endpoint details parameters response"
        
        # 执行检索
        result = await self.retrieve_api_info(query, mode="mix", top_k=5)
        
        # 提取相关信息
        context = {
            "endpoint": endpoint,
            "method": method,
            "description": self._extract_description(result),
            "parameters": self._extract_parameters(result),
            "response_schema": self._extract_response_schema(result),
            "examples": self._extract_examples(result),
            "related_endpoints": self._extract_related_endpoints(result),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return context
    
    def _extract_description(self, result: Dict[str, Any]) -> str:
        """从检索结果中提取描述"""
        chunks = result.get("chunks", [])
        if chunks:
            return chunks[0].get("content", "")[:200]
        return "无描述信息"
    
    def _extract_parameters(self, result: Dict[str, Any]) -> List[Dict]:
        """从检索结果中提取参数信息"""
        # 简化实现：从实体属性中提取
        entities = result.get("entities", [])
        parameters = []
        
        for entity in entities:
            props = entity.get("properties", {})
            if "parameters" in props:
                parameters.extend(props["parameters"])
        
        return parameters
    
    def _extract_response_schema(self, result: Dict[str, Any]) -> Dict:
        """从检索结果中提取响应schema"""
        # 简化实现
        return {
            "type": "object",
            "properties": {}
        }
    
    def _extract_examples(self, result: Dict[str, Any]) -> List[Dict]:
        """从检索结果中提取示例"""
        return []
    
    def _extract_related_endpoints(self, result: Dict[str, Any]) -> List[str]:
        """从检索结果中提取相关端点"""
        entities = result.get("entities", [])
        related = []
        
        for entity in entities:
            if entity.get("entity_type") == "api_endpoint":
                related.append(entity.get("entity_name", ""))
        
        return related[:5]
    
    async def index_api_document(
        self,
        document_path: str,
        document_type: str = "openapi"
    ) -> Dict[str, Any]:
        """
        索引API文档到知识库
        
        Args:
            document_path: 文档路径
            document_type: 文档类型
        
        Returns:
            索引结果
        """
        logger.info(f"{self.agent_name} 索引文档: {document_path}")
        
        try:
            result = await self.rag_engine.index_document(
                document_path=document_path,
                document_type=document_type,
                metadata={"indexed_by": self.agent_name}
            )
            
            return {
                "success": True,
                "document_path": document_path,
                "document_type": document_type,
                "indexed_chunks": result.get("indexed_chunks", 0),
                "extracted_entities": result.get("extracted_entities", 0),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"{self.agent_name} 索引失败: {e}", exc_info=e)
            return {
                "success": False,
                "error": str(e),
                "document_path": document_path,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "agent_name": self.agent_name,
            "agent_type": "rag_retrieval",
            "capabilities": [
                "知识库查询",
                "API文档检索",
                "上下文增强",
                "文档索引"
            ],
            "supported_modes": [
                "local", "global", "hybrid", "naive", "mix", "bypass"
            ],
            "status": "active"
        }

