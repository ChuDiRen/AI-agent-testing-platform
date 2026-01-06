"""
实体提取器 - Entity Extractor

功能：
- 从文本中提取实体（API端点、参数、认证方式等）
- 使用NER模型或LLM进行实体识别
- 支持多种实体类型
"""
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import json

from core.models import RAGEntity
from core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class EntityExtractionResult:
    """实体提取结果"""
    entities: List[RAGEntity]
    confidence: float
    processing_time: float
    method: str  # "rule_based", "ner", "llm"


class EntityExtractor:
    """
    实体提取器
    
    支持三种提取方法：
    1. 基于规则的提取（快速，适用于结构化文档）
    2. NER模型提取（中等速度，适用于半结构化文本）
    3. LLM提取（慢但准确，适用于复杂文本）
    """
    
    def __init__(self, llm_service=None):
        """
        初始化实体提取器
        
        Args:
            llm_service: LLM服务实例（可选）
        """
        self.llm_service = llm_service
        
        # 实体类型定义
        self.entity_types = {
            "API_ENDPOINT": "API端点",
            "HTTP_METHOD": "HTTP方法",
            "PARAMETER": "参数",
            "REQUEST_BODY": "请求体",
            "RESPONSE": "响应",
            "AUTH_METHOD": "认证方式",
            "STATUS_CODE": "状态码",
            "HEADER": "请求头",
            "DATA_TYPE": "数据类型",
            "ERROR_CODE": "错误码"
        }
        
        # 编译正则表达式
        self._compile_patterns()
        
        logger.info("实体提取器初始化完成")
    
    def _compile_patterns(self):
        """编译正则表达式模式"""
        self.patterns = {
            "API_ENDPOINT": [
                re.compile(r'(GET|POST|PUT|DELETE|PATCH)\s+(/[\w\-/{}:]+)'),
                re.compile(r'path:\s*["\']([/\w\-/{}:]+)["\']'),
                re.compile(r'endpoint:\s*["\']([/\w\-/{}:]+)["\']'),
            ],
            "HTTP_METHOD": [
                re.compile(r'\b(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\b'),
            ],
            "PARAMETER": [
                re.compile(r'parameter[s]?:\s*(\w+)'),
                re.compile(r'param:\s*(\w+)'),
                re.compile(r'query:\s*(\w+)'),
            ],
            "AUTH_METHOD": [
                re.compile(r'\b(JWT|OAuth|Bearer|Basic|API[_\s]?Key)\b', re.IGNORECASE),
                re.compile(r'authentication:\s*(\w+)'),
            ],
            "STATUS_CODE": [
                re.compile(r'\b(200|201|204|400|401|403|404|500|502|503)\b'),
            ],
        }
    
    async def extract_entities(
        self,
        text: str,
        method: str = "auto",
        entity_types: Optional[List[str]] = None
    ) -> EntityExtractionResult:
        """
        从文本中提取实体
        
        Args:
            text: 输入文本
            method: 提取方法（"auto", "rule_based", "ner", "llm"）
            entity_types: 要提取的实体类型列表（None表示全部）
        
        Returns:
            实体提取结果
        """
        start_time = datetime.utcnow()
        
        # 自动选择方法
        if method == "auto":
            method = self._select_method(text)
        
        # 执行提取
        if method == "rule_based":
            entities = self._extract_by_rules(text, entity_types)
        elif method == "ner":
            entities = await self._extract_by_ner(text, entity_types)
        elif method == "llm":
            entities = await self._extract_by_llm(text, entity_types)
        else:
            raise ValueError(f"未知的提取方法: {method}")
        
        # 计算处理时间
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # 计算置信度
        confidence = self._calculate_confidence(entities, method)
        
        logger.info(f"提取到 {len(entities)} 个实体，方法: {method}, 耗时: {processing_time:.2f}s")
        
        return EntityExtractionResult(
            entities=entities,
            confidence=confidence,
            processing_time=processing_time,
            method=method
        )
    
    def _select_method(self, text: str) -> str:
        """自动选择提取方法"""
        # 如果文本包含明显的结构化标记，使用规则
        if any(marker in text.lower() for marker in ["openapi", "swagger", "paths:", "get:", "post:"]):
            return "rule_based"
        
        # 如果有LLM服务，使用LLM
        if self.llm_service:
            return "llm"
        
        # 默认使用规则
        return "rule_based"
    
    def _extract_by_rules(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> List[RAGEntity]:
        """
        基于规则的实体提取
        
        Args:
            text: 输入文本
            entity_types: 要提取的实体类型
        
        Returns:
            实体列表
        """
        entities = []
        entity_types = entity_types or list(self.entity_types.keys())
        
        for entity_type in entity_types:
            if entity_type not in self.patterns:
                continue
            
            # 使用所有模式匹配
            for pattern in self.patterns[entity_type]:
                matches = pattern.finditer(text)
                for match in matches:
                    # 提取实体名称
                    if len(match.groups()) > 1:
                        entity_name = match.group(2)
                    else:
                        entity_name = match.group(1) if match.groups() else match.group(0)
                    
                    # 创建实体
                    entity = RAGEntity(
                        entity_name=entity_name,
                        entity_type=entity_type,
                        description=f"{self.entity_types[entity_type]}: {entity_name}",
                        source_id="rule_based_extraction",
                        confidence=0.8
                    )
                    entities.append(entity)
        
        # 去重
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    async def _extract_by_ner(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> List[RAGEntity]:
        """
        基于NER模型的实体提取
        
        注意：这里是占位实现，实际需要集成NER模型
        """
        logger.warning("NER模型提取尚未实现，回退到规则提取")
        return self._extract_by_rules(text, entity_types)
    
    async def _extract_by_llm(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> List[RAGEntity]:
        """
        基于LLM的实体提取
        
        Args:
            text: 输入文本
            entity_types: 要提取的实体类型
        
        Returns:
            实体列表
        """
        if not self.llm_service:
            logger.warning("LLM服务不可用，回退到规则提取")
            return self._extract_by_rules(text, entity_types)
        
        # 构建提示词
        entity_types_str = ", ".join(entity_types or list(self.entity_types.keys()))
        prompt = f"""
从以下文本中提取实体信息。

实体类型：{entity_types_str}

文本：
{text}

请以JSON格式返回提取的实体，格式如下：
{{
    "entities": [
        {{
            "entity_name": "实体名称",
            "entity_type": "实体类型",
            "description": "实体描述",
            "confidence": 0.9
        }}
    ]
}}
"""
        
        try:
            # 调用LLM
            response = await self.llm_service.generate(prompt)
            
            # 解析响应
            result = json.loads(response)
            entities = []
            
            for entity_data in result.get("entities", []):
                entity = RAGEntity(
                    entity_name=entity_data["entity_name"],
                    entity_type=entity_data["entity_type"],
                    description=entity_data["description"],
                    source_id="llm_extraction",
                    confidence=entity_data.get("confidence", 0.9)
                )
                entities.append(entity)
            
            return entities
            
        except Exception as e:
            logger.error(f"LLM提取失败: {e}", exc_info=True)
            return self._extract_by_rules(text, entity_types)
    
    def _deduplicate_entities(self, entities: List[RAGEntity]) -> List[RAGEntity]:
        """去重实体"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.entity_name, entity.entity_type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _calculate_confidence(self, entities: List[RAGEntity], method: str) -> float:
        """计算整体置信度"""
        if not entities:
            return 0.0
        
        # 基于方法的基础置信度
        base_confidence = {
            "rule_based": 0.7,
            "ner": 0.8,
            "llm": 0.9
        }.get(method, 0.5)
        
        # 基于实体数量的调整
        count_factor = min(len(entities) / 10, 1.0)
        
        # 基于实体置信度的平均
        avg_entity_confidence = sum(e.confidence for e in entities) / len(entities)
        
        # 综合置信度
        confidence = (base_confidence * 0.4 + count_factor * 0.2 + avg_entity_confidence * 0.4)
        
        return round(confidence, 2)
    
    def extract_from_openapi(self, openapi_spec: Dict[str, Any]) -> List[RAGEntity]:
        """
        从OpenAPI规范中提取实体
        
        Args:
            openapi_spec: OpenAPI规范字典
        
        Returns:
            实体列表
        """
        entities = []
        
        # 提取API端点
        paths = openapi_spec.get("paths", {})
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    continue
                
                # 创建端点实体
                endpoint_name = f"{method.upper()} {path}"
                entity = RAGEntity(
                    entity_name=endpoint_name,
                    entity_type="API_ENDPOINT",
                    description=operation.get("summary", operation.get("description", "")),
                    source_id="openapi_spec",
                    confidence=1.0
                )
                entities.append(entity)
                
                # 提取参数
                parameters = operation.get("parameters", [])
                for param in parameters:
                    param_entity = RAGEntity(
                        entity_name=param.get("name", ""),
                        entity_type="PARAMETER",
                        description=f"{param.get('in', '')} parameter: {param.get('description', '')}",
                        source_id=endpoint_name,
                        confidence=1.0
                    )
                    entities.append(param_entity)
        
        return entities

