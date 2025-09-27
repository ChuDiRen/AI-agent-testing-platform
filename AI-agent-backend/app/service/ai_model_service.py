# Copyright (c) 2025 左岚. All rights reserved.
"""
AI模型管理Service
处理AI模型相关的业务逻辑
"""

from typing import List, Optional, Dict, Any, Union, AsyncGenerator
from datetime import datetime

from sqlalchemy.orm import Session

from app.entity.ai_model import AIModel, ModelStatus
from app.repository.ai_model_repository import AIModelRepository
from app.dto.ai_model_dto import (
    AIModelCreateRequest, AIModelUpdateRequest, AIModelSearchRequest,
    AIModelResponse, AIModelListResponse, AIModelStatisticsResponse,
    AIModelTestRequest, AIModelTestResponse, AIModelUsageRecordRequest
)
from app.service.ai_client_service import (
    ai_client_service, ChatRequest, ChatMessage, MessageRole, ChatResponse
)
from app.core.logger import get_logger
from app.utils.exceptions import BusinessException

logger = get_logger(__name__)


class AIModelService:
    """AI模型Service类"""

    def __init__(self, db: Session):
        self.db = db
        self.model_repo = AIModelRepository(db)

    def create_model(self, request: AIModelCreateRequest, created_by_id: int) -> AIModelResponse:
        """创建AI模型"""
        try:
            # 检查名称是否已存在
            existing_model = self.model_repo.find_by_name(request.name)
            if existing_model:
                raise BusinessException(f"模型名称 '{request.name}' 已存在")
            
            # 创建模型实体
            model = AIModel(
                name=request.name,
                display_name=request.display_name,
                provider=request.provider.value if hasattr(request.provider, 'value') else request.provider,
                model_type=request.model_type.value if hasattr(request.model_type, 'value') else request.model_type,
                version=request.version,
                description=request.description,
                api_endpoint=request.api_endpoint,
                api_key=request.api_key,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                pricing=request.pricing,
                config=request.config,
                created_by_id=created_by_id
            )
            
            # 保存到数据库
            created_model = self.model_repo.create(model)
            
            logger.info(f"Created AI model '{created_model.name}' with id {created_model.id}")
            return self._convert_to_response(created_model)
            
        except Exception as e:
            logger.error(f"Error creating AI model: {str(e)}")
            raise

    def get_model_by_id(self, model_id: int, include_sensitive: bool = False) -> Optional[AIModelResponse]:
        """根据ID获取模型"""
        try:
            model = self.model_repo.get_by_id(model_id)
            if not model:
                return None
            
            return self._convert_to_response(model, include_sensitive)
            
        except Exception as e:
            logger.error(f"Error getting AI model by id {model_id}: {str(e)}")
            raise

    def search_models(self, request: AIModelSearchRequest) -> AIModelListResponse:
        """搜索AI模型"""
        try:
            models, total = self.model_repo.search(
                keyword=request.keyword,
                provider=request.provider.value if request.provider and hasattr(request.provider, 'value') else request.provider,
                model_type=request.model_type.value if request.model_type and hasattr(request.model_type, 'value') else request.model_type,
                status=request.status.value if request.status and hasattr(request.status, 'value') else request.status,
                created_by_id=request.created_by_id,
                start_date=request.start_date,
                end_date=request.end_date,
                skip=request.skip,
                limit=request.limit
            )
            
            # 转换为响应对象
            model_responses = [self._convert_to_response(model) for model in models]
            
            return AIModelListResponse(
                models=model_responses,
                total=total,
                page=request.page,
                page_size=request.page_size,
                total_pages=(total + request.page_size - 1) // request.page_size
            )
            
        except Exception as e:
            logger.error(f"Error searching AI models: {str(e)}")
            raise

    def get_model_statistics(self) -> AIModelStatisticsResponse:
        """获取AI模型统计信息"""
        try:
            statistics = self.model_repo.get_statistics()
            
            return AIModelStatisticsResponse(**statistics)
            
        except Exception as e:
            logger.error(f"Error getting AI model statistics: {str(e)}")
            raise

    async def test_model(self, model_id: int, request: AIModelTestRequest) -> AIModelTestResponse:
        """测试AI模型"""
        try:
            model = self.model_repo.get_by_id(model_id)
            if not model:
                raise BusinessException(f"模型 {model_id} 不存在")

            if not model.is_active():
                raise BusinessException(f"模型 {model_id} 未激活")

            test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            start_time = datetime.now()

            # 使用真实的AI客户端进行测试
            try:
                test_result = await ai_client_service.test_connection(model)

                if test_result["success"]:
                    # 进行实际的聊天测试
                    chat_request = ChatRequest(
                        messages=[ChatMessage(
                            role=MessageRole.USER,
                            content=request.test_prompt or "Hello, please respond with 'Test successful'"
                        )],
                        model_id=model_id,
                        temperature=request.test_config.get("temperature") if request.test_config else None,
                        max_tokens=50  # 测试时使用较少的token
                    )

                    chat_response = await ai_client_service.chat(model, chat_request)

                    if isinstance(chat_response, ChatResponse):
                        success = True
                        response_text = chat_response.content
                        tokens_used = chat_response.tokens_used
                        cost = chat_response.cost
                        error_message = None

                        # 记录使用情况
                        self.record_model_usage(model_id, AIModelUsageRecordRequest(
                            tokens_used=tokens_used,
                            cost=cost,
                            operation_type="test"
                        ))
                    else:
                        # 流式响应的情况
                        success = True
                        response_text = "流式响应测试成功"
                        tokens_used = 10  # 估算值
                        cost = model.get_cost_per_token() * tokens_used
                        error_message = None
                else:
                    success = False
                    response_text = None
                    tokens_used = 0
                    cost = 0.0
                    error_message = test_result.get("error", "连接测试失败")

            except Exception as e:
                success = False
                response_text = None
                tokens_used = 0
                cost = 0.0
                error_message = str(e)

            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()

            test_response = AIModelTestResponse(
                test_id=test_id,
                model_id=model_id,
                test_prompt=request.test_prompt or "Hello, please respond with 'Test successful'",
                response_text=response_text,
                tokens_used=tokens_used,
                response_time=response_time,
                cost=cost,
                success=success,
                error_message=error_message,
                metadata=request.test_config or {},
                tested_at=start_time
            )

            logger.info(f"AI model {model_id} test completed: {success}")
            return test_response

        except Exception as e:
            logger.error(f"Error testing AI model {model_id}: {str(e)}")
            raise

    async def chat_with_model(self, model_id: int, messages: List[Dict[str, str]],
                             user_id: int, stream: bool = False, **kwargs) -> Union[ChatResponse, AsyncGenerator[str, None]]:
        """与AI模型聊天"""
        try:
            model = self.model_repo.get_by_id(model_id)
            if not model:
                raise BusinessException(f"模型 {model_id} 不存在")

            if not model.is_active():
                raise BusinessException(f"模型 {model_id} 未激活")

            # 转换消息格式
            chat_messages = []
            for msg in messages:
                role = MessageRole(msg.get("role", "user"))
                content = msg.get("content", "")
                chat_messages.append(ChatMessage(role=role, content=content))

            # 创建聊天请求
            chat_request = ChatRequest(
                messages=chat_messages,
                large_model_id=model_id,
                temperature=kwargs.get("temperature"),
                max_tokens=kwargs.get("max_tokens"),
                stream=stream,
                user_id=user_id
            )

            # 调用AI客户端
            response = await ai_client_service.chat(model, chat_request)

            # 如果是完整响应，记录使用情况
            if isinstance(response, ChatResponse):
                self.record_model_usage(model_id, AIModelUsageRecordRequest(
                    tokens_used=response.tokens_used,
                    cost=response.cost,
                    operation_type="chat",
                    user_id=user_id
                ))

            return response

        except Exception as e:
            logger.error(f"Error chatting with AI model {model_id}: {str(e)}")
            raise

    def record_model_usage(self, model_id: int, request: AIModelUsageRecordRequest) -> bool:
        """记录模型使用情况"""
        try:
            model = self.model_repo.get_by_id(model_id)
            if not model:
                raise BusinessException(f"模型 {model_id} 不存在")
            
            # 更新使用统计
            model.record_usage(request.tokens_used, request.cost)
            
            # 更新数据库
            self.model_repo.update(model_id, {
                'usage_count': model.usage_count,
                'total_tokens': model.total_tokens,
                'total_cost': model.total_cost,
                'last_used_at': model.last_used_at
            })
            
            logger.info(f"Recorded usage for AI model {model_id}: {request.tokens_used} tokens, ${request.cost}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording model usage {model_id}: {str(e)}")
            raise

    def _simulate_model_test(self, model: AIModel, test_prompt: str, 
                           test_config: Dict[str, Any]) -> tuple[bool, str, int, float, str]:
        """
        模拟模型测试
        
        Returns:
            (success, response_text, tokens_used, cost, error_message)
        """
        try:
            # 模拟成功的API调用
            if "error" in test_prompt.lower():
                # 模拟错误情况
                return False, None, 0, 0.0, "模拟API错误：测试提示词包含错误标识"
            
            # 模拟成功响应
            response_text = f"这是对提示词 '{test_prompt[:50]}...' 的模拟响应。模型 {model.name} 工作正常。"
            tokens_used = len(test_prompt) + len(response_text)  # 简化的token计算
            
            # 模拟费用计算
            input_cost = len(test_prompt) * 0.0001  # 每token 0.0001美元
            output_cost = len(response_text) * 0.0002  # 每token 0.0002美元
            total_cost = input_cost + output_cost
            
            return True, response_text, tokens_used, total_cost, None
            
        except Exception as e:
            return False, None, 0, 0.0, str(e)

    def _convert_to_response(self, model: AIModel, include_sensitive: bool = False) -> AIModelResponse:
        """转换为响应对象"""
        data = model.to_dict(include_sensitive=include_sensitive)
        return AIModelResponse(**data)