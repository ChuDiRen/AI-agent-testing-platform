"""
API自动化智能体平台 - 完整配置管理

本模块提供平台的全面配置管理功能，支持：
- 多环境配置（开发、测试、预发布、生产）
- 环境变量和配置文件
- 配置验证和默认值
- 类型安全的配置访问
"""
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import os
from pydantic import BaseSettings, Field
from enum import Enum


class LogLevel(str, Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(str, Enum):
    """环境类型"""
    DEVELOPMENT = "development"  # 开发环境
    TESTING = "testing"          # 测试环境
    STAGING = "staging"          # 预发布环境
    PRODUCTION = "production"    # 生产环境


class LLMProvider(str, Enum):
    """LLM提供商"""
    OPENAI = "openai"              # OpenAI
    ANTHROPIC = "anthropic"        # Anthropic Claude
    AZURE_OPENAI = "azure_openai"  # Azure OpenAI
    LOCAL = "local"                # 本地模型


class DatabaseConfig(BaseSettings):
    """数据库配置"""
    url: str = Field(default="sqlite+aiosqlite:///./data/api_automation.db", env="DATABASE_URL", description="数据库连接URL")
    echo: bool = Field(default=False, env="DATABASE_ECHO", description="是否打印SQL语句")
    pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE", description="连接池大小")
    max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW", description="最大溢出连接数")


class LLMConfig(BaseSettings):
    """LLM配置"""
    provider: LLMProvider = Field(default=LLMProvider.OPENAI, env="LLM_PROVIDER", description="LLM提供商")
    model: str = Field(default="gpt-4-turbo-preview", env="LLM_MODEL", description="模型名称")
    api_key: str = Field(default="", env="OPENAI_API_KEY", description="API密钥")
    api_base: Optional[str] = Field(default=None, env="OPENAI_API_BASE", description="API基础URL")
    temperature: float = Field(default=0.3, env="LLM_TEMPERATURE", description="温度参数 0-1")
    max_tokens: int = Field(default=4000, env="LLM_MAX_TOKENS", description="最大token数")
    timeout: int = Field(default=60, env="LLM_TIMEOUT", description="超时时间（秒）")


class RAGConfig(BaseSettings):
    """RAG配置"""
    persist_directory: str = Field(default="./data/chromadb", env="RAG_PERSIST_DIR", description="持久化目录")
    collection_name: str = Field(default="api_knowledge", env="RAG_COLLECTION_NAME", description="集合名称")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="RAG_EMBEDDING_MODEL", description="嵌入模型")
    chunk_size: int = Field(default=512, env="RAG_CHUNK_SIZE", description="文本块大小")
    chunk_overlap: int = Field(default=50, env="RAG_CHUNK_OVERLAP", description="文本块重叠大小")
    enable_multimodal: bool = Field(default=False, env="RAG_ENABLE_MULTIMODAL", description="是否启用多模态")
    retrieval_mode: str = Field(default="mix", env="RAG_RETRIEVAL_MODE", description="检索模式: local/global/hybrid/naive/mix/bypass")


class MCPConfig(BaseSettings):
    """MCP服务器配置"""
    rag_server_port: int = Field(default=8001, env="RAG_SERVER_PORT", description="RAG服务器端口")
    chart_server_port: int = Field(default=8002, env="CHART_SERVER_PORT", description="图表服务器端口")
    automation_server_port: int = Field(default=8003, env="AUTOMATION_SERVER_PORT", description="自动化服务器端口")
    enable_rag_server: bool = Field(default=True, env="ENABLE_RAG_SERVER", description="是否启用RAG服务器")
    enable_chart_server: bool = Field(default=True, env="ENABLE_CHART_SERVER", description="是否启用图表服务器")
    enable_automation_server: bool = Field(default=True, env="ENABLE_AUTOMATION_SERVER", description="是否启用自动化服务器")


class ChartConfig(BaseSettings):
    """图表配置"""
    base_url: str = Field(default="http://localhost:3000", env="CHART_BASE_URL", description="图表服务基础URL")
    default_theme: str = Field(default="default", env="CHART_DEFAULT_THEME", description="默认主题")
    default_width: int = Field(default=800, env="CHART_DEFAULT_WIDTH", description="默认宽度")
    default_height: int = Field(default=600, env="CHART_DEFAULT_HEIGHT", description="默认高度")
    enable_sse: bool = Field(default=True, env="CHART_ENABLE_SSE", description="是否启用SSE流式传输")
    export_formats: List[str] = Field(default=["png", "svg", "pdf"], env="CHART_EXPORT_FORMATS", description="导出格式列表")


class TestConfig(BaseSettings):
    """测试配置"""
    default_framework: str = Field(default="playwright", env="TEST_DEFAULT_FRAMEWORK", description="默认测试框架")
    default_language: str = Field(default="typescript", env="TEST_DEFAULT_LANGUAGE", description="默认编程语言")
    timeout: int = Field(default=30000, env="TEST_TIMEOUT", description="超时时间（毫秒）")
    retry_count: int = Field(default=3, env="TEST_RETRY_COUNT", description="重试次数")
    parallel_execution: bool = Field(default=True, env="TEST_PARALLEL_EXECUTION", description="是否并行执行")
    report_formats: List[str] = Field(default=["html", "json"], env="TEST_REPORT_FORMATS", description="报告格式列表")


class SecurityConfig(BaseSettings):
    """安全配置"""
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY", description="密钥（生产环境必须修改）")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES", description="访问令牌过期时间（分钟）")
    enable_cors: bool = Field(default=True, env="ENABLE_CORS", description="是否启用CORS")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS", description="CORS允许的源列表")
    rate_limit_enabled: bool = Field(default=False, env="RATE_LIMIT_ENABLED", description="是否启用速率限制")
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS", description="速率限制请求数")
    rate_limit_window: int = Field(default=3600, env="RATE_LIMIT_WINDOW", description="速率限制时间窗口（秒）")


class LoggingConfig(BaseSettings):
    """日志配置"""
    level: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL", description="日志级别")
    format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT", description="日志格式")
    file_path: Optional[str] = Field(default=None, env="LOG_FILE_PATH", description="日志文件路径")
    max_file_size: int = Field(default=10485760, env="LOG_MAX_FILE_SIZE", description="日志文件最大大小（字节）")  # 10MB
    backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT", description="日志备份数量")
    enable_rich: bool = Field(default=True, env="LOG_ENABLE_RICH", description="是否启用Rich终端输出")


class PlatformConfig(BaseSettings):
    """平台主配置"""

    # 环境配置
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT", description="运行环境")
    debug: bool = Field(default=False, env="DEBUG", description="调试模式")

    # 服务器配置
    host: str = Field(default="0.0.0.0", env="HOST", description="服务器主机地址")
    port: int = Field(default=8000, env="PORT", description="服务器端口")
    workers: int = Field(default=1, env="WORKERS", description="工作进程数")
    reload: bool = Field(default=False, env="RELOAD", description="热重载")

    # 子配置模块
    database: DatabaseConfig = Field(default_factory=DatabaseConfig, description="数据库配置")
    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM配置")
    rag: RAGConfig = Field(default_factory=RAGConfig, description="RAG配置")
    mcp: MCPConfig = Field(default_factory=MCPConfig, description="MCP服务器配置")
    charts: ChartConfig = Field(default_factory=ChartConfig, description="图表配置")
    testing: TestConfig = Field(default_factory=TestConfig, description="测试配置")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="安全配置")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="日志配置")

    # 路径配置
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent, description="基础目录")
    data_dir: Path = Field(default_factory=lambda: Path("./data"), description="数据目录")
    logs_dir: Path = Field(default_factory=lambda: Path("./logs"), description="日志目录")
    uploads_dir: Path = Field(default_factory=lambda: Path("./uploads"), description="上传目录")
    outputs_dir: Path = Field(default_factory=lambda: Path("./outputs"), description="输出目录")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()

    def _ensure_directories(self):
        """确保所有必需的目录存在"""
        directories = [
            self.data_dir,
            self.logs_dir,
            self.uploads_dir,
            self.outputs_dir,
            self.base_dir / "data" / "chromadb",
            self.base_dir / "data" / "sessions",
            self.base_dir / "data" / "reports"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def is_development(self) -> bool:
        """检查是否为开发模式"""
        return self.environment == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        """检查是否为生产模式"""
        return self.environment == Environment.PRODUCTION

    def get_database_url(self) -> str:
        """获取数据库URL"""
        return self.database.url

    def get_llm_config(self) -> Dict[str, Any]:
        """获取LLM配置字典"""
        return {
            "provider": self.llm.provider.value,
            "model": self.llm.model,
            "api_key": self.llm.api_key,
            "api_base": self.llm.api_base,
            "temperature": self.llm.temperature,
            "max_tokens": self.llm.max_tokens,
            "timeout": self.llm.timeout
        }

    def get_rag_config(self) -> Dict[str, Any]:
        """获取RAG配置字典"""
        return {
            "persist_directory": self.rag.persist_directory,
            "collection_name": self.rag.collection_name,
            "embedding_model": self.rag.embedding_model,
            "chunk_size": self.rag.chunk_size,
            "chunk_overlap": self.rag.chunk_overlap,
            "enable_multimodal": self.rag.enable_multimodal,
            "retrieval_mode": self.rag.retrieval_mode
        }

    def get_mcp_servers_config(self) -> Dict[str, Any]:
        """获取MCP服务器配置"""
        return {
            "rag_server": {
                "enabled": self.mcp.enable_rag_server,
                "port": self.mcp.rag_server_port
            },
            "chart_server": {
                "enabled": self.mcp.enable_chart_server,
                "port": self.mcp.chart_server_port
            },
            "automation_server": {
                "enabled": self.mcp.enable_automation_server,
                "port": self.mcp.automation_server_port
            }
        }

    def validate_config(self) -> List[str]:
        """验证配置并返回问题列表"""
        issues = []

        # 检查必需的API密钥
        if self.llm.provider == LLMProvider.OPENAI and not self.llm.api_key:
            issues.append("使用OpenAI提供商时需要API密钥")

        if self.llm.provider == LLMProvider.ANTHROPIC and not self.llm.api_key:
            issues.append("使用Anthropic提供商时需要API密钥")

        # 检查生产环境的安全设置
        if self.is_production():
            if self.security.secret_key == "your-secret-key-change-in-production":
                issues.append("生产环境必须修改密钥")

            if self.security.cors_origins == ["*"]:
                issues.append("生产环境应限制CORS源")

        # 检查目录权限
        if not self.data_dir.exists():
            issues.append(f"数据目录不存在: {self.data_dir}")

        return issues


# 全局配置实例
config: Optional[PlatformConfig] = None


def get_config(**kwargs) -> PlatformConfig:
    """获取全局配置实例"""
    global config
    if config is None:
        config = PlatformConfig(**kwargs)
    return config


def load_config_from_file(config_path: Union[str, Path]) -> PlatformConfig:
    """从文件加载配置"""
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    return PlatformConfig(_env_file=str(config_path))


def create_sample_env_file(output_path: Union[str, Path] = ".env.example") -> None:
    """创建示例.env文件"""
def create_sample_env_file(output_path: Union[str, Path] = ".env.example") -> None:
    """创建示例.env文件"""
    env_content = """# API自动化智能体平台 - 环境配置

# ==================== 环境配置 ====================
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
WORKERS=1
RELOAD=false

# ==================== 数据库配置 ====================
DATABASE_URL=sqlite+aiosqlite:///./data/api_automation.db
DATABASE_ECHO=false
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# ==================== LLM配置 ====================
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_API_BASE=
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=4000
LLM_TIMEOUT=60

# ==================== RAG配置 ====================
RAG_PERSIST_DIR=./data/chromadb
RAG_COLLECTION_NAME=api_knowledge
RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=50
RAG_ENABLE_MULTIMODAL=false
RAG_RETRIEVAL_MODE=mix

# ==================== MCP服务器配置 ====================
ENABLE_RAG_SERVER=true
RAG_SERVER_PORT=8001
ENABLE_CHART_SERVER=true
CHART_SERVER_PORT=8002
ENABLE_AUTOMATION_SERVER=true
AUTOMATION_SERVER_PORT=8003

# ==================== 图表配置 ====================
CHART_BASE_URL=http://localhost:3000
CHART_DEFAULT_THEME=default
CHART_DEFAULT_WIDTH=800
CHART_DEFAULT_HEIGHT=600
CHART_ENABLE_SSE=true

# ==================== 测试配置 ====================
TEST_DEFAULT_FRAMEWORK=playwright
TEST_DEFAULT_LANGUAGE=typescript
TEST_TIMEOUT=30000
TEST_RETRY_COUNT=3
TEST_PARALLEL_EXECUTION=true

# ==================== 安全配置 ====================
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENABLE_CORS=true
CORS_ORIGINS=*
RATE_LIMIT_ENABLED=false
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# ==================== 日志配置 ====================
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/platform.log
LOG_MAX_FILE_SIZE=10485760
LOG_BACKUP_COUNT=5
LOG_ENABLE_RICH=true
"""

    output_path = Path(output_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(env_content)


def validate_environment() -> bool:
    """验证当前环境配置"""
    config = get_config()
    issues = config.validate_config()

    if issues:
        print("配置问题:")
        for issue in issues:
            print(f"  - {issue}")
        return False

    return True

