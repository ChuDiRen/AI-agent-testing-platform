"""
向量嵌入服务
"""
from typing import List, Optional
from abc import ABC, abstractmethod

from core.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__)


class EmbeddingProvider(ABC):
    """嵌入模型提供者抽象基类"""

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量嵌入文档

        Args:
            texts: 文本列表

        Returns:
            嵌入向量列表
        """
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        嵌入单个查询

        Args:
            text: 查询文本

        Returns:
            嵌入向量
        """
        pass

    @property
    @abstractmethod
    def embedding_dimension(self) -> int:
        """嵌入维度"""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI嵌入模型"""

    def __init__(
        self,
        model: str = "text-embedding-ada-002",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        初始化OpenAI嵌入模型

        Args:
            model: 模型名称
            api_key: API密钥
            base_url: API基础URL
        """
        try:
            from openai import OpenAI

            self.client = OpenAI(
                api_key=api_key or settings.OPENAI_API_KEY,
                base_url=base_url or settings.OPENAI_BASE_URL
            )
            self.model = model

            # 设置模型维度
            self._dimension_map = {
                "text-embedding-ada-002": 1536,
                "text-embedding-3-small": 1536,
                "text-embedding-3-large": 3072,
            }
            self._dimension = self._dimension_map.get(model, 1536)

            logger.info(f"OpenAI嵌入模型初始化成功: {model}")

        except ImportError:
            logger.warning("openai库未安装，OpenAI嵌入功能不可用")
            raise ImportError("请安装 openai: pip install openai")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )

            embeddings = [item.embedding for item in response.data]
            logger.debug(f"OpenAI嵌入成功: {len(texts)} 个文档")
            return embeddings

        except Exception as e:
            logger.error(f"OpenAI嵌入失败: {str(e)}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )

            embedding = response.data[0].embedding
            logger.debug(f"OpenAI查询嵌入成功")
            return embedding

        except Exception as e:
            logger.error(f"OpenAI查询嵌入失败: {str(e)}")
            raise

    @property
    def embedding_dimension(self) -> int:
        """嵌入维度"""
        return self._dimension


class LocalEmbeddingProvider(EmbeddingProvider):
    """本地嵌入模型（使用sentence-transformers）"""

    def __init__(
        self,
        model_name: str = "BAAI/bge-large-zh-v1.5",
        device: Optional[str] = None
    ):
        """
        初始化本地嵌入模型

        Args:
            model_name: 模型名称
            device: 设备（cuda, cpu, auto）
        """
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(model_name, device=device)
            self._dimension = self.model.get_sentence_embedding_dimension()

            logger.info(f"本地嵌入模型初始化成功: {model_name} (维度: {self._dimension})")

        except ImportError:
            logger.warning("sentence-transformers未安装，本地嵌入功能不可用")
            raise ImportError("请安装 sentence-transformers: pip install sentence-transformers")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文档"""
        try:
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 100
            )

            # 转换为列表
            embedding_list = embeddings.tolist()

            logger.debug(f"本地嵌入成功: {len(texts)} 个文档")
            return embedding_list

        except Exception as e:
            logger.error(f"本地嵌入失败: {str(e)}")
            raise

    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询"""
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()

        except Exception as e:
            logger.error(f"本地查询嵌入失败: {str(e)}")
            raise

    @property
    def embedding_dimension(self) -> int:
        """嵌入维度"""
        return self._dimension


class EmbeddingService:
    """嵌入服务"""

    def __init__(self, provider: Optional[EmbeddingProvider] = None):
        """
        初始化嵌入服务

        Args:
            provider: 嵌入提供者，如果为None则根据配置自动选择
        """
        if provider:
            self.provider = provider
        else:
            self.provider = self._create_provider_from_config()

        logger.info("嵌入服务初始化完成")

    def _create_provider_from_config(self) -> EmbeddingProvider:
        """根据配置创建嵌入提供者"""
        provider_type = settings.EMBEDDING_PROVIDER.lower()

        if provider_type == "openai":
            return OpenAIEmbeddingProvider(
                model=settings.EMBEDDING_MODEL,
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )
        elif provider_type == "local":
            return LocalEmbeddingProvider(
                model_name=settings.EMBEDDING_MODEL
            )
        else:
            logger.warning(f"未知的嵌入提供者类型: {provider_type}，使用本地模型")
            return LocalEmbeddingProvider(model_name=settings.EMBEDDING_MODEL)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量嵌入文档

        Args:
            texts: 文本列表

        Returns:
            嵌入向量列表
        """
        if not texts:
            return []

        # 分批处理以避免超过API限制
        batch_size = 100
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.provider.embed_documents(batch)
            all_embeddings.extend(embeddings)

        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        """
        嵌入单个查询

        Args:
            text: 查询文本

        Returns:
            嵌入向量
        """
        return self.provider.embed_query(text)

    @property
    def embedding_dimension(self) -> int:
        """嵌入维度"""
        return self.provider.embedding_dimension
