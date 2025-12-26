"""需求分析工具 - 支持URL获取和知识库集成

功能:
1. 自动识别URL链接并获取需求文档内容
2. 支持多种来源: 知识库、Confluence、普通网页
3. 支持文本和URL两种输入方式
"""
import re
import json
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from dataclasses import dataclass
from enum import Enum

import requests
from langchain_core.tools import tool


class SourceType(Enum):
    """来源类型"""
    TEXT = "text"           # 纯文本
    URL = "url"             # 普通URL
    CONFLUENCE = "confluence"  # Confluence页面
    NOTION = "notion"       # Notion页面
    YUQUE = "yuque"         # 语雀文档
    FEISHU = "feishu"       # 飞书文档


@dataclass
class FetchResult:
    """获取结果"""
    success: bool
    content: str
    source_type: SourceType
    url: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class RequirementFetcher:
    """需求文档获取器"""
    
    # URL模式识别
    URL_PATTERNS = {
        SourceType.CONFLUENCE: [
            r'confluence\..*\.com',
            r'.*\.atlassian\.net/wiki',
        ],
        SourceType.NOTION: [
            r'notion\.so',
            r'notion\.site',
        ],
        SourceType.YUQUE: [
            r'yuque\.com',
        ],
        SourceType.FEISHU: [
            r'feishu\.cn',
            r'larksuite\.com',
        ],
    }
    
    def __init__(
        self,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None,
        confluence_token: Optional[str] = None,
        notion_token: Optional[str] = None,
    ):
        """初始化
        
        Args:
            timeout: 请求超时时间
            headers: 自定义请求头
            confluence_token: Confluence API Token
            notion_token: Notion API Token
        """
        self.timeout = timeout
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.confluence_token = confluence_token
        self.notion_token = notion_token
    
    def fetch(self, url_or_text: str) -> FetchResult:
        """获取需求文档内容
        
        Args:
            url_or_text: URL或纯文本
            
        Returns:
            获取结果
        """
        # 检测是否为URL
        if self._is_url(url_or_text):
            source_type = self._detect_source_type(url_or_text)
            return self._fetch_from_url(url_or_text, source_type)
        else:
            # 纯文本直接返回
            return FetchResult(
                success=True,
                content=url_or_text,
                source_type=SourceType.TEXT,
            )
    
    def _is_url(self, text: str) -> bool:
        """检测是否为URL"""
        text = text.strip()
        if text.startswith(('http://', 'https://')):
            return True
        # 检测常见域名模式
        url_pattern = r'^(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b'
        return bool(re.match(url_pattern, text))
    
    def _detect_source_type(self, url: str) -> SourceType:
        """检测URL来源类型"""
        for source_type, patterns in self.URL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return source_type
        return SourceType.URL
    
    def _fetch_from_url(self, url: str, source_type: SourceType) -> FetchResult:
        """从URL获取内容"""
        try:
            if source_type == SourceType.CONFLUENCE:
                return self._fetch_confluence(url)
            elif source_type == SourceType.NOTION:
                return self._fetch_notion(url)
            else:
                return self._fetch_generic_url(url)
        except Exception as e:
            return FetchResult(
                success=False,
                content="",
                source_type=source_type,
                url=url,
                error=str(e),
            )
    
    def _fetch_generic_url(self, url: str) -> FetchResult:
        """获取普通URL内容"""
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            
            # 尝试解析HTML提取正文
            content = self._extract_text_from_html(response.text)
            
            return FetchResult(
                success=True,
                content=content,
                source_type=SourceType.URL,
                url=url,
                metadata={"status_code": response.status_code},
            )
        except requests.RequestException as e:
            return FetchResult(
                success=False,
                content="",
                source_type=SourceType.URL,
                url=url,
                error=str(e),
            )
    
    def _fetch_confluence(self, url: str) -> FetchResult:
        """获取Confluence页面内容"""
        # 尝试使用API获取
        if self.confluence_token:
            try:
                # 解析页面ID
                page_id = self._extract_confluence_page_id(url)
                if page_id:
                    api_url = self._build_confluence_api_url(url, page_id)
                    headers = {
                        **self.headers,
                        "Authorization": f"Bearer {self.confluence_token}",
                        "Accept": "application/json",
                    }
                    response = requests.get(api_url, headers=headers, timeout=self.timeout)
                    if response.ok:
                        data = response.json()
                        content = self._parse_confluence_response(data)
                        return FetchResult(
                            success=True,
                            content=content,
                            source_type=SourceType.CONFLUENCE,
                            url=url,
                            metadata={"page_id": page_id},
                        )
            except Exception:
                pass
        
        # 回退到普通URL获取
        return self._fetch_generic_url(url)
    
    def _fetch_notion(self, url: str) -> FetchResult:
        """获取Notion页面内容"""
        # Notion需要API Token
        if self.notion_token:
            try:
                page_id = self._extract_notion_page_id(url)
                if page_id:
                    api_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
                    headers = {
                        "Authorization": f"Bearer {self.notion_token}",
                        "Notion-Version": "2022-06-28",
                    }
                    response = requests.get(api_url, headers=headers, timeout=self.timeout)
                    if response.ok:
                        data = response.json()
                        content = self._parse_notion_response(data)
                        return FetchResult(
                            success=True,
                            content=content,
                            source_type=SourceType.NOTION,
                            url=url,
                            metadata={"page_id": page_id},
                        )
            except Exception:
                pass
        
        # 回退到普通URL获取
        return self._fetch_generic_url(url)
    
    def _extract_text_from_html(self, html: str) -> str:
        """从HTML中提取文本"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # 获取文本
            text = soup.get_text(separator='\n', strip=True)
            
            # 清理多余空行
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return '\n'.join(lines)
        except ImportError:
            # 如果没有BeautifulSoup，使用简单的正则
            text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', '', text)
            return text.strip()
    
    def _extract_confluence_page_id(self, url: str) -> Optional[str]:
        """从Confluence URL中提取页面ID"""
        # 常见格式: /pages/viewpage.action?pageId=123456
        match = re.search(r'pageId=(\d+)', url)
        if match:
            return match.group(1)
        
        # 另一种格式: /wiki/spaces/SPACE/pages/123456/Title
        match = re.search(r'/pages/(\d+)', url)
        if match:
            return match.group(1)
        
        return None
    
    def _build_confluence_api_url(self, url: str, page_id: str) -> str:
        """构建Confluence API URL"""
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        return f"{base_url}/wiki/rest/api/content/{page_id}?expand=body.storage"
    
    def _parse_confluence_response(self, data: Dict[str, Any]) -> str:
        """解析Confluence API响应"""
        title = data.get("title", "")
        body = data.get("body", {}).get("storage", {}).get("value", "")
        
        # 从HTML中提取文本
        content = self._extract_text_from_html(body)
        
        return f"# {title}\n\n{content}"
    
    def _extract_notion_page_id(self, url: str) -> Optional[str]:
        """从Notion URL中提取页面ID"""
        # 格式: https://www.notion.so/Page-Title-32位ID
        match = re.search(r'([a-f0-9]{32})$', url.replace('-', ''))
        if match:
            return match.group(1)
        return None
    
    def _parse_notion_response(self, data: Dict[str, Any]) -> str:
        """解析Notion API响应"""
        blocks = data.get("results", [])
        content_parts = []
        
        for block in blocks:
            block_type = block.get("type", "")
            block_data = block.get(block_type, {})
            
            if "rich_text" in block_data:
                text = "".join(
                    t.get("plain_text", "") 
                    for t in block_data["rich_text"]
                )
                if text:
                    content_parts.append(text)
        
        return "\n".join(content_parts)


# ============== LangChain Tool 定义 ==============

@tool
def analyze_requirements_from_input(url_or_text: str) -> str:
    """需求文档获取与分析工具
    
    支持URL和文本两种输入方式:
    - URL: 自动获取网页内容
    - 文本: 直接返回
    
    Args:
        url_or_text: URL链接或需求文本
        
    Returns:
        需求文档内容
    """
    fetcher = RequirementFetcher()
    result = fetcher.fetch(url_or_text)
    
    if result.success:
        return result.content
    else:
        return f"获取失败: {result.error}"


@tool
def fetch_url_content(url: str) -> str:
    """获取URL内容
    
    Args:
        url: 网页URL
        
    Returns:
        网页文本内容
    """
    fetcher = RequirementFetcher()
    result = fetcher._fetch_generic_url(url)
    
    if result.success:
        return result.content
    else:
        return f"获取失败: {result.error}"


@tool
def fetch_confluence_page(url: str, token: Optional[str] = None) -> str:
    """获取Confluence页面内容
    
    Args:
        url: Confluence页面URL
        token: API Token (可选)
        
    Returns:
        页面内容
    """
    fetcher = RequirementFetcher(confluence_token=token)
    result = fetcher._fetch_confluence(url)
    
    if result.success:
        return result.content
    else:
        return f"获取失败: {result.error}"


@tool
def parse_requirement(requirement_text: str) -> Dict[str, Any]:
    """解析需求文本，提取结构化信息
    
    分析需求文本，识别功能点、业务规则、接口信息等。
    
    Args:
        requirement_text: 需求描述文本
        
    Returns:
        结构化的需求信息
    """
    result = {
        "功能点": [],
        "业务规则": [],
        "接口信息": {},
        "约束条件": [],
        "测试类型建议": "API",
    }
    
    # 识别功能点（以动词开头的句子）
    func_patterns = [
        r'支持(.+?)(?:[。；,]|$)',
        r'实现(.+?)(?:[。；,]|$)',
        r'提供(.+?)(?:[。；,]|$)',
        r'能够(.+?)(?:[。；,]|$)',
    ]
    for pattern in func_patterns:
        matches = re.findall(pattern, requirement_text)
        result["功能点"].extend(matches)
    
    # 识别业务规则（包含"如果"、"当"、"必须"等关键词）
    rule_patterns = [
        r'如果(.+?)(?:则|就)(.+?)(?:[。；]|$)',
        r'当(.+?)时[，,](.+?)(?:[。；]|$)',
        r'必须(.+?)(?:[。；,]|$)',
        r'不能(.+?)(?:[。；,]|$)',
    ]
    for pattern in rule_patterns:
        matches = re.findall(pattern, requirement_text)
        for match in matches:
            if isinstance(match, tuple):
                result["业务规则"].append(" -> ".join(match))
            else:
                result["业务规则"].append(match)
    
    # 识别接口信息
    if "接口" in requirement_text or "API" in requirement_text:
        result["测试类型建议"] = "API"
        # 提取HTTP方法
        methods = re.findall(r'(GET|POST|PUT|DELETE|PATCH)', requirement_text, re.IGNORECASE)
        if methods:
            result["接口信息"]["methods"] = list(set(methods))
        # 提取URL路径
        paths = re.findall(r'(/[a-zA-Z0-9/_-]+)', requirement_text)
        if paths:
            result["接口信息"]["paths"] = list(set(paths))
    
    # 识别约束条件
    constraint_patterns = [
        r'长度[不]?[超过|小于|大于|等于](\d+)',
        r'范围[为是]?(\d+)[到至-](\d+)',
        r'最[大小]值?[为是]?(\d+)',
    ]
    for pattern in constraint_patterns:
        matches = re.findall(pattern, requirement_text)
        result["约束条件"].extend([str(m) for m in matches])
    
    # 去重
    result["功能点"] = list(set(result["功能点"]))
    result["业务规则"] = list(set(result["业务规则"]))
    result["约束条件"] = list(set(result["约束条件"]))
    
    return result


@tool
def extract_test_points(requirement_text: str, analysis_result: Optional[str] = None) -> Dict[str, Any]:
    """从需求中提取测试点
    
    基于需求文本和分析结果，提取需要测试的关键点。
    
    Args:
        requirement_text: 需求描述文本
        analysis_result: 需求分析结果（可选）
        
    Returns:
        测试点列表和分类
    """
    test_points = {
        "正常流程": [],
        "边界值": [],
        "异常处理": [],
        "安全测试": [],
        "性能测试": [],
    }
    
    # 正常流程测试点
    if "登录" in requirement_text:
        test_points["正常流程"].append("正确用户名密码登录成功")
    if "注册" in requirement_text:
        test_points["正常流程"].append("正确信息注册成功")
    if "查询" in requirement_text:
        test_points["正常流程"].append("正常条件查询返回正确结果")
    if "创建" in requirement_text or "新增" in requirement_text:
        test_points["正常流程"].append("正确参数创建成功")
    if "修改" in requirement_text or "更新" in requirement_text:
        test_points["正常流程"].append("正确参数修改成功")
    if "删除" in requirement_text:
        test_points["正常流程"].append("删除操作执行成功")
    
    # 边界值测试点
    if re.search(r'长度|字符|范围|最[大小]', requirement_text):
        test_points["边界值"].extend([
            "最小值边界",
            "最大值边界",
            "边界值-1",
            "边界值+1",
        ])
    
    # 异常处理测试点
    test_points["异常处理"].extend([
        "必填参数为空",
        "参数格式错误",
        "参数类型错误",
        "资源不存在",
    ])
    
    # 安全测试点
    if "密码" in requirement_text or "登录" in requirement_text:
        test_points["安全测试"].extend([
            "SQL注入攻击",
            "XSS攻击",
            "密码错误次数限制",
        ])
    
    # 性能测试点
    if "并发" in requirement_text or "性能" in requirement_text:
        test_points["性能测试"].extend([
            "并发请求处理",
            "响应时间要求",
            "大数据量处理",
        ])
    
    # 统计
    total = sum(len(points) for points in test_points.values())
    
    return {
        "test_points": test_points,
        "total_count": total,
        "categories": list(test_points.keys()),
    }


# ============== 工具集合 ==============

REQUIREMENT_TOOLS = [
    analyze_requirements_from_input,
    fetch_url_content,
    fetch_confluence_page,
    parse_requirement,
    extract_test_points,
]

__all__ = [
    "RequirementFetcher",
    "FetchResult",
    "SourceType",
    "analyze_requirements_from_input",
    "fetch_url_content",
    "fetch_confluence_page",
    "parse_requirement",
    "extract_test_points",
    "REQUIREMENT_TOOLS",
]
