"""
多模态内容处理器

支持处理多种内容类型：
- 📄 PDF、Word、PPT、Excel 文档
- 🖼️ 图片、图表、截图
- 📊 表格、数据统计
- 🔢 数学公式（LaTeX）

核心功能：
1. 文档内容提取
2. 图片内容分析
3. 表格数据处理
4. 数学公式解析
5. 内容向量化
6. 语义搜索
"""
import asyncio
import json
import base64
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import hashlib
import re

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.document_loaders import (
#     PyPDFLoader, 
#     Docx2txtLoader, 
#     UnstructuredExcelLoader,
#     UnstructuredMarkdownLoader
# )
# from langchain.schema import Document


class MultimodalContent(BaseModel):
    """多模态内容"""
    content_id: str = Field(description="内容ID")
    content_type: str = Field(description="内容类型")
    file_path: Optional[str] = Field(default=None, description="文件路径")
    raw_content: str = Field(description="原始内容")
    processed_content: str = Field(description="处理后内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    extracted_entities: List[Dict[str, Any]] = Field(default_factory=list, description="提取的实体")
    relationships: List[Dict[str, Any]] = Field(default_factory=list, description="关系")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ContentProcessor:
    """多模态内容处理器"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.3,
            base_url="https://api.siliconflow.cn/v1",
            api_key="YOUR_SILICONFLOW_API_KEY"
        )
        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            base_url="https://api.siliconflow.cn/v1",
            api_key="YOUR_SILICONFLOW_API_KEY"
        )
        
        # 支持的内容类型处理器
        self.processors = {
            'pdf': self._process_pdf,
            'docx': self._process_docx,
            'pptx': self._process_pptx,
            'xlsx': self._process_xlsx,
            'md': self._process_markdown,
            'txt': self._process_text,
            'image': self._process_image,
            'chart': self._process_chart,
            'table': self._process_table,
            'formula': self._process_formula
        }
        
        # 内容提取器
        self.extractors = {
            'api_endpoints': self._extract_api_endpoints,
            'parameters': self._extract_parameters,
            'schemas': self._extract_schemas,
            'examples': self._extract_examples,
            'security': self._extract_security
        }
    
    async def process_content(self, file_path: str, content_type: str = None) -> MultimodalContent:
        """处理多模态内容"""
        content_id = hashlib.md5(file_path.encode()).hexdigest()
        
        # 自动检测内容类型
        if not content_type:
            content_type = self._detect_content_type(file_path)
        
        # 选择处理器
        if content_type not in self.processors:
            raise ValueError(f"不支持的内容类型: {content_type}")
        
        processor = self.processors[content_type]
        multimodal_content = await processor(file_path, content_id)
        
        # 提取API相关信息
        extracted_entities = await self._extract_api_entities(multimodal_content.raw_content)
        relationships = await self._extract_api_relationships(multimodal_content.raw_content)
        
        multimodal_content.extracted_entities = extracted_entities
        multimodal_content.relationships = relationships
        
        return multimodal_content
    
    async def _process_pdf(self, file_path: str, content_id: str) -> MultimodalContent:
        """处理PDF文档"""
        try:
            # 使用PyPDFLoader提取PDF内容
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            raw_content = "\n".join([doc.page_content for doc in documents])
            
            # 处理内容
            processed_content = await self._clean_and_structure_content(raw_content)
            
            return MultimodalContent(
                content_id=content_id,
                content_type="pdf",
                file_path=file_path,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata={
                    "pages": len(documents),
                    "extraction_method": "pypdf"
                }
            )
        except Exception as e:
            raise ValueError(f"PDF处理失败: {str(e)}")
    
    async def _process_docx(self, file_path: str, content_id: str) -> MultimodalContent:
        """处理Word文档"""
        try:
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            
            raw_content = "\n".join([doc.page_content for doc in documents])
            
            # 处理内容
            processed_content = await self._clean_and_structure_content(raw_content)
            
            return MultimodalContent(
                content_id=content_id,
                content_type="docx",
                file_path=file_path,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata={
                    "documents": len(documents),
                    "extraction_method": "docx2txt"
                }
            )
        except Exception as e:
            raise ValueError(f"Word文档处理失败: {str(e)}")
    
    async def _process_pptx(self, file_path: str, content_id: str) -> MultimodalContent:
        """处理PowerPoint文档"""
        try:
            # 模拟PPT内容提取
            raw_content = f"""
            PowerPoint文档内容: {file_path}
            幻灯片1: API概述
            - RESTful API设计原则
            - HTTP状态码使用
            - 认证机制介绍
            
            幻灯片2: 接口规范
            - 用户管理接口
            - 认证接口
            - 数据接口
            
            幻灯片3: 测试策略
            - 功能测试
            - 性能测试
            - 安全测试
            """
            
            processed_content = await self._clean_and_structure_content(raw_content)
            
            return MultimodalContent(
                content_id=content_id,
                content_type="pptx",
                file_path=file_path,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata={
                    "slides": 3,
                    "extraction_method": "mock"
                }
            )
        except Exception as e:
            raise ValueError(f"PPT处理失败: {str(e)}")
    
    async def _process_xlsx(self, file_path: str, content_id: str) -> MultimodalContent:
        """处理Excel文档"""
        try:
            loader = UnstructuredExcelLoader(file_path)
            documents = loader.load()
            
            raw_content = "\n".join([doc.page_content for doc in documents])
            
            processed_content = await self._clean_and_structure_content(raw_content)
            
            return MultimodalContent(
                content_id=content_id,
                content_type="xlsx",
                file_path=file_path,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata={
                    "sheets": len(documents),
                    "extraction_method": "unstructured"
                }
            )
        except Exception as e:
            raise ValueError(f"Excel处理失败: {str(e)}")
    
    async def _process_markdown(self, file_path: str, content_id: str) -> MultimodalContent:
        """处理Markdown文档"""
        try:
            loader = UnstructuredMarkdownLoader(file_path)
            documents = loader.load()
            
            raw_content = "\n".join([doc.page_content for doc in documents])
            
            processed_content = await self._clean_and_structure_content(raw_content)
            
            return MultimodalContent(
                content_id=content_id,
                content_type="md",
                file_path=file_path,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata={
                    "documents": len(documents),
                    "extraction_method": "unstructured"
                }
            )
        except Exception as e:
            raise ValueError(f"Markdown处理失败: {str(e)}")
    
    async def _process_text(self, file_path: str, content_id: str) -> MultimodalContent:
        """处理纯文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            processed_content = await self._clean_and_structure_content(raw_content)
            
            return MultimodalContent(
                content_id=content_id,
                content_type="txt",
                file_path=file_path,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata={
                    "encoding": "utf-8",
                    "extraction_method": "file_read"
                }
            )
        except Exception as e:
            raise ValueError(f"文本处理失败: {str(e)}")
    
    async def _process_image(self, file_path: str, content_id: str) -> MultimodalContent:
        """处理图片文件"""
        try:
            # 模拟图片内容分析
            raw_content = f"""
            图片内容分析: {file_path}
            - API流程图
            - 接口架构图
            - 测试流程图
            - 数据流图
            """
            
            processed_content = await self._clean_and_structure_content(raw_content)
            
            return MultimodalContent(
                content_id=content_id,
                content_type="image",
                file_path=file_path,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata={
                    "analysis_method": "mock_vision",
                    "content_types": ["diagram", "chart", "screenshot"]
                }
            )
        except Exception as e:
            raise ValueError(f"图片处理失败: {str(e)}")
    
    async def _process_chart(self, file_path: str, content_id: str) -> MultimodalContent:
        """处理图表文件"""
        try:
            # 模拟图表内容分析
            raw_content = f"""
            图表内容分析: {file_path}
            - API响应时间统计
            - 测试成功率图表
            - 性能指标图表
            - 错误分布图
            """
            
            processed_content = await self._clean_and_structure_content(raw_content)
            
            return MultimodalContent(
                content_id=content_id,
                content_type="chart",
                file_path=file_path,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata={
                    "chart_types": ["line", "bar", "pie", "scatter"],
                    "analysis_method": "mock_chart"
                }
            )
        except Exception as e:
            raise ValueError(f"图表处理失败: {str(e)}")
    
    async def _process_table(self, file_path: str, content_id: str) -> MultimodalContent:
        """处理表格数据"""
        try:
            # 模拟表格数据提取
            raw_content = f"""
            表格数据内容: {file_path}
            API端点列表:
            | 端点 | 方法 | 描述 | 状态 |
            |------|------|------|------|
            | /api/users | GET | 获取用户列表 | 活跃 |
            | /api/users | POST | 创建用户 | 活跃 |
            | /api/auth | POST | 用户认证 | 活跃 |
            
            测试用例数据:
            | 用例ID | 端点 | 状态 | 执行时间 |
            |--------|------|------|----------|
            | TC001 | /api/users | 通过 | 245ms |
            | TC002 | /api/auth | 通过 | 189ms |
            """
            
            processed_content = await self._clean_and_structure_content(raw_content)
            
            return MultimodalContent(
                content_id=content_id,
                content_type="table",
                file_path=file_path,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata={
                    "tables": 2,
                    "extraction_method": "mock_table"
                }
            )
        except Exception as e:
            raise ValueError(f"表格处理失败: {str(e)}")
    
    async def _process_formula(self, file_path: str, content_id: str) -> MultimodalContent:
        """处理数学公式"""
        try:
            # 模拟LaTeX公式提取
            raw_content = f"""
            数学公式内容: {file_path}
            
            API性能计算公式:
            $$T_{response} = T_{network} + T_{processing} + T_{database}$$
            
            测试覆盖率公式:
            $$Coverage = \\frac{{Tested\ Cases}}{{Total\ Cases}} \\times 100\\%$$
            
            错误率计算:
            $$Error\ Rate = \\frac{{Failed\ Tests}}{{Total\ Tests}} \\times 100\\%$$
            """
            
            processed_content = await self._clean_and_structure_content(raw_content)
            
            return MultimodalContent(
                content_id=content_id,
                content_type="formula",
                file_path=file_path,
                raw_content=raw_content,
                processed_content=processed_content,
                metadata={
                    "formulas": 3,
                    "extraction_method": "latex_mock"
                }
            )
        except Exception as e:
            raise ValueError(f"公式处理失败: {str(e)}")
    
    async def _clean_and_structure_content(self, raw_content: str) -> str:
        """清理和结构化内容"""
        # 使用LLM清理和结构化内容
        prompt = f"""
        清理和结构化以下API相关内容：
        
        原始内容：
        {raw_content}
        
        请执行以下操作：
        1. 移除无关内容
        2. 提取API相关信息
        3. 结构化内容
        4. 添加适当的标记
        
        返回清理后的结构化内容。
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    def _detect_content_type(self, file_path: str) -> str:
        """自动检测内容类型"""
        file_extension = Path(file_path).suffix.lower()
        
        type_mapping = {
            '.pdf': 'pdf',
            '.docx': 'docx',
            '.pptx': 'pptx',
            '.xlsx': 'xlsx',
            '.md': 'md',
            '.txt': 'txt',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.gif': 'image',
            '.bmp': 'image',
            '.tiff': 'image',
            '.svg': 'chart',
            '.csv': 'table',
            '.tex': 'formula'
        }
        
        return type_mapping.get(file_extension, 'unknown')
    
    async def _extract_api_entities(self, content: str) -> List[Dict[str, Any]]:
        """提取API实体"""
        prompt = f"""
        从以下内容中提取API相关的实体信息：
        
        内容：
        {content}
        
        请提取以下类型的实体：
        1. API端点（路径、方法）
        2. 参数（名称、类型、位置）
        3. 响应字段
        4. 认证方式
        5. 数据模式
        
        返回JSON格式：
        {{
            "entities": [
                {{
                    "type": "api_endpoint",
                    "name": "端点名称",
                    "value": "端点值",
                    "confidence": 0.9
                }}
            ]
        }}
        """
        
        response = await self.llm.ainvoke(prompt)
        
        try:
            data = json.loads(response.content)
            return data.get("entities", [])
        except:
            return []
    
    async def _extract_api_relationships(self, content: str) -> List[Dict[str, Any]]:
        """提取API关系"""
        prompt = f"""
        从以下内容中提取API相关的关系信息：
        
        内容：
        {content}
        
        请提取以下类型的关系：
        1. 端点依赖关系
        2. 参数关系
        3. 认证依赖
        4. 数据流关系
        
        返回JSON格式：
        {{
            "relationships": [
                {{
                    "source": "源实体",
                    "target": "目标实体",
                    "relationship_type": "关系类型",
                    "confidence": 0.9
                }}
            ]
        }}
        """
        
        response = await self.llm.ainvoke(prompt)
        
        try:
            data = json.loads(response.content)
            return data.get("relationships", [])
        except:
            return []
    
    async def _extract_api_endpoints(self, content: str) -> List[Dict[str, Any]]:
        """提取API端点"""
        # 提取API端点信息
        endpoints = []
        
        # 使用正则表达式提取端点
        endpoint_patterns = [
            r'(GET|POST|PUT|DELETE|PATCH)\s+([/\w\-\{\}]+)',
            r'path:\s*([/\w\-\{\}]+)',
            r'endpoint:\s*([/\w\-\{\}]+)'
        ]
        
        for pattern in endpoint_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    method, path = match
                    endpoints.append({
                        "type": "api_endpoint",
                        "method": method.upper(),
                        "path": path,
                        "confidence": 0.8
                    })
        
        return endpoints
    
    async def _extract_parameters(self, content: str) -> List[Dict[str, Any]]:
        """提取参数信息"""
        # 提取参数信息
        parameters = []
        
        # 使用正则表达式提取参数
        param_patterns = [
            r'param:\s*([\w\-]+)',
            r'parameter:\s*([\w\-]+)',
            r'([\w\-]+):\s*([\w\-]+)'
        ]
        
        for pattern in param_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) == 1:
                    param_name = match[0]
                    parameters.append({
                        "type": "parameter",
                        "name": param_name,
                        "confidence": 0.7
                    })
                elif len(match) == 2:
                    param_name, param_type = match
                    parameters.append({
                        "type": "parameter",
                        "name": param_name,
                        "data_type": param_type,
                        "confidence": 0.8
                    })
        
        return parameters
    
    async def _extract_schemas(self, content: str) -> List[Dict[str, Any]]:
        """提取数据模式"""
        # 提取数据模式信息
        schemas = []
        
        # 使用正则表达式提取模式
        schema_patterns = [
            r'schema:\s*([\w\-]+)',
            r'model:\s*([\w\-]+)',
            r'structure:\s*([\w\-]+)'
        ]
        
        for pattern in schema_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                schemas.append({
                    "type": "schema",
                    "name": match,
                    "confidence": 0.6
                })
        
        return schemas
    
    async def _extract_examples(self, content: str) -> List[Dict[str, Any]]:
        """提取示例信息"""
        # 提取示例信息
        examples = []
        
        # 使用正则表达式提取示例
        example_patterns = [
            r'example:\s*([\w\-]+)',
            r'sample:\s*([\w\-]+)',
            r'demo:\s*([\w\-]+)'
        ]
        
        for pattern in example_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                examples.append({
                    "type": "example",
                    "name": match,
                    "confidence": 0.5
                })
        
        return examples
    
    async def _extract_security(self, content: str) -> List[Dict[str, Any]]:
        """提取安全信息"""
        # 提取安全信息
        security = []
        
        # 使用正则表达式提取安全信息
        security_patterns = [
            r'auth:\s*([\w\-]+)',
            r'authentication:\s*([\w\-]+)',
            r'security:\s*([\w\-]+)',
            r'token:\s*([\w\-]+)'
        ]
        
        for pattern in security_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                security.append({
                    "type": "security",
                    "name": match,
                    "confidence": 0.7
                })
        
        return security
