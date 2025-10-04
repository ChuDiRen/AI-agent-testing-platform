# Copyright (c) 2025 左岚. All rights reserved.
"""向量存储服务 - Qdrant集成"""
from typing import List, Dict, Any, Optional, Tuple
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
)
from sentence_transformers import SentenceTransformer
import numpy as np

from app.core.config import settings


class VectorStore:
    """向量存储服务"""
    
    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.model_name = "BAAI/bge-large-zh-v1.5"  # 中文优化的向量模型
        self.vector_dimension = 1024  # BGE-large-zh-v1.5的向量维度
    
    def initialize(self):
        """初始化向量存储"""
        if self.client is None:
            # 连接Qdrant (本地模式)
            self.client = QdrantClient(path="./qdrant_data")  # 本地存储
            # 如果使用远程Qdrant服务器:
            # self.client = QdrantClient(host="localhost", port=6333)
        
        if self.embedding_model is None:
            # 加载向量化模型
            self.embedding_model = SentenceTransformer(self.model_name)
            print(f"✅ 向量模型加载成功: {self.model_name}")
    
    def create_collection(self, collection_name: str, vector_dimension: int = None) -> bool:
        """创建向量集合"""
        try:
            self.initialize()
            
            # 检查集合是否已存在
            collections = self.client.get_collections().collections
            if any(c.name == collection_name for c in collections):
                print(f"⚠️  集合已存在: {collection_name}")
                return True
            
            # 创建集合
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_dimension or self.vector_dimension,
                    distance=Distance.COSINE  # 余弦相似度
                )
            )
            print(f"✅ 创建集合成功: {collection_name}")
            return True
        except Exception as e:
            print(f"❌ 创建集合失败: {e}")
            return False
    
    def delete_collection(self, collection_name: str) -> bool:
        """删除向量集合"""
        try:
            self.initialize()
            self.client.delete_collection(collection_name)
            print(f"✅ 删除集合成功: {collection_name}")
            return True
        except Exception as e:
            print(f"❌ 删除集合失败: {e}")
            return False
    
    def embed_text(self, text: str) -> List[float]:
        """文本向量化"""
        self.initialize()
        vector = self.embedding_model.encode(text, normalize_embeddings=True)
        return vector.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量文本向量化"""
        self.initialize()
        vectors = self.embedding_model.encode(texts, normalize_embeddings=True, batch_size=32)
        return vectors.tolist()
    
    def add_documents(
        self,
        collection_name: str,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """添加文档到向量库"""
        try:
            self.initialize()
            
            # 生成ID
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in texts]
            
            # 向量化
            vectors = self.embed_texts(texts)
            
            # 构建Points
            points = []
            for i, (text, vector, metadata) in enumerate(zip(texts, vectors, metadatas)):
                point = PointStruct(
                    id=ids[i],
                    vector=vector,
                    payload={
                        "text": text,
                        **metadata
                    }
                )
                points.append(point)
            
            # 批量插入
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            print(f"✅ 添加 {len(points)} 个文档到 {collection_name}")
            return ids
        except Exception as e:
            print(f"❌ 添加文档失败: {e}")
            raise
    
    def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.5,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """搜索相似文档"""
        try:
            self.initialize()
            
            # 查询向量化
            query_vector = self.embed_text(query)
            
            # 构建过滤条件
            query_filter = None
            if filter_conditions:
                conditions = []
                for key, value in filter_conditions.items():
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
                query_filter = Filter(must=conditions)
            
            # 搜索
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=query_filter
            )
            
            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append((
                    result.id,  # 向量ID
                    result.score,  # 相似度分数
                    result.payload  # 元数据
                ))
            
            return formatted_results
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            raise
    
    def delete_documents(
        self,
        collection_name: str,
        ids: List[str]
    ) -> bool:
        """删除文档"""
        try:
            self.initialize()
            self.client.delete(
                collection_name=collection_name,
                points_selector=ids
            )
            print(f"✅ 删除 {len(ids)} 个文档")
            return True
        except Exception as e:
            print(f"❌ 删除文档失败: {e}")
            return False
    
    def delete_by_filter(
        self,
        collection_name: str,
        filter_conditions: Dict[str, Any]
    ) -> bool:
        """根据条件删除文档"""
        try:
            self.initialize()
            
            # 构建过滤条件
            conditions = []
            for key, value in filter_conditions.items():
                conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=value))
                )
            
            self.client.delete(
                collection_name=collection_name,
                points_selector=Filter(must=conditions)
            )
            print(f"✅ 根据条件删除文档成功")
            return True
        except Exception as e:
            print(f"❌ 删除文档失败: {e}")
            return False
    
    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """获取集合信息"""
        try:
            self.initialize()
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            print(f"❌ 获取集合信息失败: {e}")
            return None
    
    def list_collections(self) -> List[str]:
        """列出所有集合"""
        try:
            self.initialize()
            collections = self.client.get_collections().collections
            return [c.name for c in collections]
        except Exception as e:
            print(f"❌ 列出集合失败: {e}")
            return []


# 全局向量存储实例
vector_store = VectorStore()

