"""
关系提取器 - Relationship Extractor

功能：
- 从文本中提取实体之间的关系
- 支持规则、模式匹配和LLM三种方法
- 识别API依赖、参数关系、认证关系等
"""
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import json

from core.models import RAGRelationship, RAGEntity
from core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class RelationshipExtractionResult:
    """关系提取结果"""
    relationships: List[RAGRelationship]
    confidence: float
    processing_time: float
    method: str


class RelationshipExtractor:
    """
    关系提取器
    
    支持三种提取方法：
    1. 基于规则的提取（快速）
    2. 基于模式的提取（中等）
    3. 基于LLM的提取（准确）
    """
    
    def __init__(self, llm_service=None):
        """初始化关系提取器"""
        self.llm_service = llm_service
        
        # 关系类型定义
        self.relationship_types = {
            "DEPENDS_ON": "依赖关系",
            "REQUIRES": "需要关系",
            "RETURNS": "返回关系",
            "USES": "使用关系",
            "AUTHENTICATES_WITH": "认证关系",
            "VALIDATES": "验证关系",
            "CALLS": "调用关系",
            "INHERITS": "继承关系"
        }
        
        # 编译关系模式
        self._compile_patterns()
        
        logger.info("关系提取器初始化完成")
    
    def _compile_patterns(self):
        """编译关系模式"""
        self.patterns = {
            "DEPENDS_ON": [
                re.compile(r'(\w+)\s+depends\s+on\s+(\w+)', re.IGNORECASE),
                re.compile(r'(\w+)\s+requires\s+(\w+)', re.IGNORECASE),
            ],
            "RETURNS": [
                re.compile(r'(\w+)\s+returns?\s+(\w+)', re.IGNORECASE),
                re.compile(r'response:\s*(\w+)', re.IGNORECASE),
            ],
            "AUTHENTICATES_WITH": [
                re.compile(r'(\w+)\s+authenticates?\s+with\s+(\w+)', re.IGNORECASE),
                re.compile(r'(\w+)\s+uses?\s+(JWT|OAuth|Bearer)', re.IGNORECASE),
            ],
            "CALLS": [
                re.compile(r'(\w+)\s+calls?\s+(\w+)', re.IGNORECASE),
                re.compile(r'(\w+)\s+invokes?\s+(\w+)', re.IGNORECASE),
            ]
        }
    
    async def extract_relationships(
        self,
        text: str,
        entities: List[RAGEntity],
        method: str = "auto"
    ) -> RelationshipExtractionResult:
        """
        从文本中提取关系
        
        Args:
            text: 输入文本
            entities: 已提取的实体列表
            method: 提取方法
        
        Returns:
            关系提取结果
        """
        start_time = datetime.utcnow()
        
        # 自动选择方法
        if method == "auto":
            method = "llm" if self.llm_service else "rule_based"
        
        # 执行提取
        if method == "rule_based":
            relationships = self._extract_by_rules(text, entities)
        elif method == "pattern":
            relationships = self._extract_by_patterns(text, entities)
        elif method == "llm":
            relationships = await self._extract_by_llm(text, entities)
        else:
            raise ValueError(f"未知的提取方法: {method}")
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        confidence = self._calculate_confidence(relationships, method)
        
        logger.info(f"提取到 {len(relationships)} 个关系，方法: {method}")
        
        return RelationshipExtractionResult(
            relationships=relationships,
            confidence=confidence,
            processing_time=processing_time,
            method=method
        )
    
    def _extract_by_rules(
        self,
        text: str,
        entities: List[RAGEntity]
    ) -> List[RAGRelationship]:
        """基于规则的关系提取"""
        relationships = []
        entity_names = {e.entity_name for e in entities}
        
        # 使用模式匹配
        for rel_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = pattern.finditer(text)
                for match in matches:
                    if len(match.groups()) >= 2:
                        src = match.group(1)
                        tgt = match.group(2)
                        
                        # 验证实体存在
                        if src in entity_names and tgt in entity_names:
                            rel = RAGRelationship(
                                src_id=src,
                                tgt_id=tgt,
                                description=self.relationship_types[rel_type],
                                weight=0.8,
                                keywords=[rel_type.lower()]
                            )
                            relationships.append(rel)
        
        return self._deduplicate_relationships(relationships)
    
    def _extract_by_patterns(
        self,
        text: str,
        entities: List[RAGEntity]
    ) -> List[RAGRelationship]:
        """基于模式的关系提取"""
        # 目前与规则提取相同
        return self._extract_by_rules(text, entities)
    
    async def _extract_by_llm(
        self,
        text: str,
        entities: List[RAGEntity]
    ) -> List[RAGRelationship]:
        """基于LLM的关系提取"""
        if not self.llm_service:
            return self._extract_by_rules(text, entities)
        
        entity_list = [e.entity_name for e in entities]
        prompt = f"""
从以下文本中提取实体之间的关系。

实体列表：{', '.join(entity_list)}

文本：
{text}

请以JSON格式返回关系，格式如下：
{{
    "relationships": [
        {{
            "source": "源实体",
            "target": "目标实体",
            "type": "关系类型",
            "description": "关系描述",
            "confidence": 0.9
        }}
    ]
}}
"""
        
        try:
            response = await self.llm_service.generate(prompt)
            result = json.loads(response)
            relationships = []
            
            for rel_data in result.get("relationships", []):
                rel = RAGRelationship(
                    src_id=rel_data["source"],
                    tgt_id=rel_data["target"],
                    description=rel_data["description"],
                    weight=rel_data.get("confidence", 0.9),
                    keywords=[rel_data.get("type", "").lower()]
                )
                relationships.append(rel)
            
            return relationships
            
        except Exception as e:
            logger.error(f"LLM关系提取失败: {e}")
            return self._extract_by_rules(text, entities)
    
    def _deduplicate_relationships(
        self,
        relationships: List[RAGRelationship]
    ) -> List[RAGRelationship]:
        """去重关系"""
        seen = set()
        unique = []
        
        for rel in relationships:
            key = (rel.src_id, rel.tgt_id, rel.description)
            if key not in seen:
                seen.add(key)
                unique.append(rel)
        
        return unique
    
    def _calculate_confidence(
        self,
        relationships: List[RAGRelationship],
        method: str
    ) -> float:
        """计算整体置信度"""
        if not relationships:
            return 0.0
        
        base = {"rule_based": 0.7, "pattern": 0.75, "llm": 0.9}.get(method, 0.5)
        avg_weight = sum(r.weight for r in relationships) / len(relationships)
        
        return round((base * 0.5 + avg_weight * 0.5), 2)
    
    def extract_from_openapi(
        self,
        openapi_spec: Dict[str, Any],
        entities: List[RAGEntity]
    ) -> List[RAGRelationship]:
        """从OpenAPI规范中提取关系"""
        relationships = []
        entity_map = {e.entity_name: e for e in entities}
        
        paths = openapi_spec.get("paths", {})
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method.upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    continue
                
                endpoint_name = f"{method.upper()} {path}"
                
                # 参数关系
                for param in operation.get("parameters", []):
                    param_name = param.get("name", "")
                    if endpoint_name in entity_map and param_name in entity_map:
                        rel = RAGRelationship(
                            src_id=endpoint_name,
                            tgt_id=param_name,
                            description="需要参数",
                            weight=1.0,
                            keywords=["parameter", "requires"]
                        )
                        relationships.append(rel)
                
                # 认证关系
                security = operation.get("security", [])
                for sec in security:
                    for auth_name in sec.keys():
                        if endpoint_name in entity_map:
                            rel = RAGRelationship(
                                src_id=endpoint_name,
                                tgt_id=auth_name,
                                description="需要认证",
                                weight=1.0,
                                keywords=["authentication", "security"]
                            )
                            relationships.append(rel)
        
        return relationships

