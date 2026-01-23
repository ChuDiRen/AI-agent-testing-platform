"""
智能问答服务（RAG + LLM）
"""
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from rag.rag_engine import RAGEngine
from services.llm_service import LLMService
from core.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__)


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(description="角色：user, assistant, system")
    content: str = Field(description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class ChatCitation(BaseModel):
    """引用信息"""
    chunk_id: str = Field(description="块ID")
    doc_id: int = Field(description="文档ID")
    doc_name: str = Field(description="文档名称")
    page_number: Optional[int] = Field(default=None, description="页码")
    text: str = Field(description="引用的文本")
    score: float = Field(description="相似度分数")


class ChatResponse(BaseModel):
    """聊天响应"""
    answer: str = Field(description="AI回答")
    citations: List[ChatCitation] = Field(default_factory=list, description="引用列表")
    session_id: str = Field(description="会话ID")
    message_id: str = Field(description="消息ID")
    model: str = Field(description="使用的模型")
    processing_time: float = Field(description="处理时间（秒）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ChatService:
    """智能问答服务"""

    def __init__(
        self,
        rag_engine: RAGEngine,
        llm_service: LLMService,
        system_prompt: Optional[str] = None
    ):
        """
        初始化聊天服务

        Args:
            rag_engine: RAG引擎
            llm_service: LLM服务
            system_prompt: 系统提示词
        """
        self.rag_engine = rag_engine
        self.llm_service = llm_service
        self.system_prompt = system_prompt or self._get_default_system_prompt()

        # 会话历史（生产环境应该使用Redis等持久化存储）
        self.chat_history: Dict[str, List[ChatMessage]] = {}

        logger.info("智能问答服务初始化完成")

    def _get_default_system_prompt(self) -> str:
        """获取默认系统提示词"""
        return """你是一个专业的知识库助手，能够基于提供的上下文信息回答用户的问题。

请遵循以下规则：
1. 仅基于提供的上下文信息回答问题，不要编造或添加外部信息
2. 如果上下文中没有相关信息，请明确说明"根据提供的文档无法找到相关信息"
3. 回答要准确、简洁、有条理
4. 必要时可以引用具体的文档内容和页码
5. 使用清晰易懂的语言，避免专业术语或在使用时进行解释
6. 如果问题涉及多个方面，可以分点回答

上下文信息：
{context}

用户问题：
{question}
"""

    async def chat(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        top_k: int = None,
        score_threshold: float = None,
        stream: bool = False
    ) -> ChatResponse:
        """
        智能问答

        Args:
            query: 用户问题
            session_id: 会话ID（如果为None则创建新会话）
            user_id: 用户ID
            top_k: 检索结果数量
            score_threshold: 相似度阈值
            stream: 是否流式返回

        Returns:
            聊天响应
        """
        start_time = datetime.now()

        # 生成或使用现有的会话ID
        if not session_id:
            session_id = str(uuid.uuid4())

        # 生成消息ID
        message_id = str(uuid.uuid4())

        logger.info(f"开始处理聊天请求: session_id={session_id}, message_id={message_id}, query='{query}'")

        try:
            # 1. 向量检索
            logger.info("步骤1: 向量检索")
            search_results = await self.rag_engine.search(
                query=query,
                top_k=top_k or settings.TOP_K,
                score_threshold=score_threshold or settings.SIMILARITY_THRESHOLD
            )

            # 2. 构建上下文
            logger.info("步骤2: 构建上下文")
            context = self._build_context(search_results)

            # 3. 构建提示词
            logger.info("步骤3: 构建提示词")
            prompt = self._build_prompt(query, context)

            # 4. 生成回答
            logger.info("步骤4: 生成回答")
            answer = await self.llm_service.generate(prompt)

            # 5. 构建引用
            logger.info("步骤5: 构建引用")
            citations = self._build_citations(search_results)

            # 6. 保存到历史
            logger.info("步骤6: 保存历史")
            self._save_to_history(session_id, query, answer, citations)

            # 计算处理时间
            processing_time = (datetime.now() - start_time).total_seconds()

            # 构建响应
            response = ChatResponse(
                answer=answer,
                citations=citations,
                session_id=session_id,
                message_id=message_id,
                model=self.llm_service.model_name,
                processing_time=processing_time,
                metadata={
                    "search_results_count": len(search_results),
                    "citations_count": len(citations),
                    "context_length": len(context),
                    "user_id": user_id,
                    "timestamp": start_time.isoformat()
                }
            )

            logger.info(f"聊天请求处理完成: session_id={session_id}, message_id={message_id}, time={processing_time:.2f}s")

            return response

        except Exception as e:
            logger.error(f"聊天请求处理失败: {str(e)}")
            raise

    async def chat_with_history(
        self,
        query: str,
        session_id: str,
        user_id: Optional[int] = None,
        top_k: int = None,
        score_threshold: float = None
    ) -> ChatResponse:
        """
        带历史记录的聊天

        Args:
            query: 用户问题
            session_id: 会话ID
            user_id: 用户ID
            top_k: 检索结果数量
            score_threshold: 相似度阈值

        Returns:
            聊天响应
        """
        # 获取会话历史
        history = self.chat_history.get(session_id, [])

        # 构建对话消息
        messages = []

        # 添加系统消息
        messages.append({
            "role": "system",
            "content": self.system_prompt
        })

        # 添加历史消息
        for msg in history[-10:]:  # 保留最近10条消息
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # 添加当前问题
        messages.append({
            "role": "user",
            "content": query
        })

        # 使用chat方法
        response = await self.chat(
            query=query,
            session_id=session_id,
            user_id=user_id,
            top_k=top_k,
            score_threshold=score_threshold
        )

        return response

    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        构建上下文

        Args:
            search_results: 搜索结果列表

        Returns:
            上下文字符串
        """
        if not search_results:
            return "没有找到相关的文档内容。"

        context_parts = []
        for i, result in enumerate(search_results, 1):
            metadata = result.get("metadata", {})
            text = result.get("text", "")

            context_part = f"\n片段 {i}：\n{text}\n"
            if "document_id" in metadata:
                context_part += f"（来源：文档ID {metadata['document_id']}"
                if "page_number" in metadata:
                    context_part += f"，页码：{metadata['page_number']}"
                context_part += "）\n"

            context_parts.append(context_part)

        return "\n".join(context_parts)

    def _build_prompt(self, query: str, context: str) -> str:
        """
        构建提示词

        Args:
            query: 用户问题
            context: 上下文

        Returns:
            提示词
        """
        prompt = self.system_prompt.format(
            context=context,
            question=query
        )

        return prompt

    def _build_citations(self, search_results: List[Dict[str, Any]]) -> List[ChatCitation]:
        """
        构建引用列表

        Args:
            search_results: 搜索结果列表

        Returns:
            引用列表
        """
        citations = []

        for result in search_results:
            metadata = result.get("metadata", {})

            citation = ChatCitation(
                chunk_id=metadata.get("chunk_id", ""),
                doc_id=metadata.get("document_id", 0),
                doc_name=metadata.get("doc_name", "未知文档"),
                page_number=metadata.get("page_number"),
                text=result.get("text", "")[:500],  # 限制长度
                score=result.get("score", 0.0)
            )

            citations.append(citation)

        return citations

    def _save_to_history(
        self,
        session_id: str,
        query: str,
        answer: str,
        citations: List[ChatCitation]
    ):
        """
        保存到历史记录

        Args:
            session_id: 会话ID
            query: 用户问题
            answer: AI回答
            citations: 引用列表
        """
        if session_id not in self.chat_history:
            self.chat_history[session_id] = []

        # 添加用户消息
        user_message = ChatMessage(
            role="user",
            content=query
        )

        # 添加助手消息（包含引用）
        assistant_content = answer
        if citations:
            assistant_content += "\n\n引用来源：\n"
            for i, citation in enumerate(citations, 1):
                assistant_content += f"{i}. {citation.doc_name}"
                if citation.page_number:
                    assistant_content += f" (页码: {citation.page_number})"
                assistant_content += f" [相似度: {citation.score:.2f}]\n"

        assistant_message = ChatMessage(
            role="assistant",
            content=assistant_content
        )

        self.chat_history[session_id].extend([user_message, assistant_message])

        # 限制历史长度（保留最近20条消息）
        if len(self.chat_history[session_id]) > 20:
            self.chat_history[session_id] = self.chat_history[session_id][-20:]

    def get_chat_history(self, session_id: str) -> List[ChatMessage]:
        """
        获取聊天历史

        Args:
            session_id: 会话ID

        Returns:
            消息列表
        """
        return self.chat_history.get(session_id, [])

    def clear_chat_history(self, session_id: str) -> bool:
        """
        清空聊天历史

        Args:
            session_id: 会话ID

        Returns:
            是否成功
        """
        if session_id in self.chat_history:
            del self.chat_history[session_id]
            logger.info(f"清空聊天历史: session_id={session_id}")
            return True
        return False

    async def stream_chat(
        self,
        query: str,
        session_id: Optional[str] = None,
        user_id: Optional[int] = None,
        top_k: int = None
    ):
        """
        流式聊天（生成器）

        Args:
            query: 用户问题
            session_id: 会话ID
            user_id: 用户ID
            top_k: 检索结果数量

        Yields:
            流式响应片段
        """
        # TODO: 实现流式聊天
        # 需要LLM提供者支持流式输出
        yield {"type": "error", "message": "流式聊天功能尚未实现"}
