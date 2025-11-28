"""测试用例生成器 - 多智能体协作版本"""
from typing import Optional

from langchain_openai import ChatOpenAI

from .agents.writer_agent import WriterProgressHook
from .config import Config
from .models import TestCaseState
from .supervisor import TestCaseSupervisor


class TestCaseGeneratorV3:
    """测试用例生成器 - 4个专家智能体 + Supervisor协调"""

    def __init__(
        self,
        config: Optional[Config] = None,
        enable_middleware: bool = True,
        enable_human_review: bool = False,
        enable_persistence: bool = True,
    ):
        self.config = config or Config()
        self.enable_middleware = enable_middleware
        self.enable_human_review = enable_human_review
        self.enable_persistence = enable_persistence

        def parse_model(model_str: str) -> tuple[str, str]:
            """provider:model_name -> (model_name, base_url)"""
            if ":" in model_str:
                provider, model_name = model_str.split(":", 1)
                if provider == "deepseek":
                    return model_name, "https://api.deepseek.com"
                elif provider == "siliconflow":
                    return model_name, "https://api.siliconflow.cn/v1"
            return model_str, None

        reader_model_name, reader_base_url = parse_model(self.config.reader_model)
        writer_model_name, writer_base_url = parse_model(self.config.writer_model)
        reviewer_model_name, reviewer_base_url = parse_model(self.config.reviewer_model)

        self.reader_model = ChatOpenAI(
            model=reader_model_name, temperature=0.3, api_key=self.config.api_key,
            base_url=reader_base_url, timeout=120.0, max_retries=3, request_timeout=120.0)
        self.writer_model = ChatOpenAI(
            model=writer_model_name, temperature=0.7, api_key=self.config.api_key,
            base_url=writer_base_url, timeout=240.0, max_retries=3, request_timeout=240.0)
        self.reviewer_model = ChatOpenAI(
            model=reviewer_model_name, temperature=0.3, api_key=self.config.api_key,
            base_url=reviewer_base_url, timeout=120.0, max_retries=3, request_timeout=120.0)
        
        # 上下文压缩模型（使用轻量级模型）
        self.summarization_model = ChatOpenAI(
            model=reader_model_name, temperature=0.1, api_key=self.config.api_key,
            base_url=reader_base_url, timeout=60.0, max_retries=2)
        
        self.supervisor = TestCaseSupervisor(
            reader_model=self.reader_model,
            writer_model=self.writer_model,
            reviewer_model=self.reviewer_model,
            summarization_model=self.summarization_model,
            enable_middleware=self.enable_middleware,
            enable_human_review=self.enable_human_review,
            enable_persistence=self.enable_persistence,
            db_path=str(self.config.testcases_db) if self.enable_persistence else None,
        )
    
    async def generate(
        self,
        requirement: str,
        test_type: str = "API",
        max_iterations: int = 2,
        writer_status_hook: Optional[WriterProgressHook] = None,
    ) -> TestCaseState:
        """requirement: 需求描述, test_type: API/Web/App, max_iterations: 最大迭代次数"""
        state = TestCaseState(requirement=requirement, test_type=test_type, max_iterations=max_iterations)
        return await self.supervisor.run(state, writer_status_hook=writer_status_hook)
    
    def get_result(self, state: TestCaseState) -> dict:
        """state -> 结果字典"""
        return {"requirement": state.requirement, "test_type": state.test_type,
                "analysis": state.analysis, "test_points": state.test_points,
                "testcases": state.testcases, "review": state.review,
                "iteration": state.iteration, "completed": state.completed}
    
    async def batch_generate(self, api_list: list, max_concurrent: int = 5, max_iterations: int = 1):
        """批量并行生成"""
        from .batch_processor import BatchProcessor, BatchConfig
        processor = BatchProcessor(self, BatchConfig(max_concurrent=max_concurrent, max_iterations=max_iterations))
        return await processor.process_batch(api_list)
    
    async def batch_generate_from_swagger(
        self, swagger_url: str, max_apis: Optional[int] = None,
        max_concurrent: int = 5, max_iterations: int = 1, test_type: str = "API",
    ):
        """从Swagger批量生成"""
        from .batch_processor import BatchProcessor, BatchConfig
        processor = BatchProcessor(self, BatchConfig(max_concurrent=max_concurrent, max_iterations=max_iterations))
        return await processor.process_swagger(swagger_url, max_apis)


# 全局实例
generator = TestCaseGeneratorV3(enable_middleware=True, enable_human_review=False, enable_persistence=True)

