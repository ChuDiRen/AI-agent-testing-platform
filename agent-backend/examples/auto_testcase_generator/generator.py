"""测试用例生成器 V3 - 多智能体协作版本
基于 LangGraph 1.0 + create_agent + middlewareV1
"""
from typing import Optional
from langchain_openai import ChatOpenAI
from .models import TestCaseState
from .supervisor import TestCaseSupervisor
from .config import Config


class TestCaseGeneratorV3:
    """测试用例生成器 V3 - 多智能体协作架构

    架构:
    - 4个专家智能体: Analyzer, TestPointDesigner, Writer, Reviewer
    - 1个Supervisor协调者: 调度智能体执行顺序
    - middlewareV1: 上下文工程优化 (消息过滤、状态同步、动态注入)
    - 人工审核: 在关键步骤暂停等待确认
    - 持久化存储: 保存生成历史到数据库
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        enable_middleware: bool = True,
        enable_human_review: bool = False,
        enable_persistence: bool = True,
    ):
        """初始化生成器

        Args:
            config: 配置对象,如果为None则使用默认配置
            enable_middleware: 是否启用 middlewareV1
            enable_human_review: 是否启用人工审核
            enable_persistence: 是否启用持久化存储
        """
        self.config = config or Config()
        self.enable_middleware = enable_middleware
        self.enable_human_review = enable_human_review
        self.enable_persistence = enable_persistence

        # 解析模型配置 (格式: provider:model_name)
        def parse_model(model_str: str) -> tuple[str, str]:
            if ":" in model_str:
                provider, model_name = model_str.split(":", 1)
                if provider == "deepseek":
                    return model_name, "https://api.deepseek.com"
            return model_str, None

        reader_model_name, reader_base_url = parse_model(self.config.reader_model)
        writer_model_name, writer_base_url = parse_model(self.config.writer_model)
        reviewer_model_name, reviewer_base_url = parse_model(self.config.reviewer_model)

        # 初始化3个模型
        self.reader_model = ChatOpenAI(
            model=reader_model_name,
            temperature=0.3,
            api_key=self.config.api_key,
            base_url=reader_base_url,
        )

        self.writer_model = ChatOpenAI(
            model=writer_model_name,
            temperature=0.7,
            api_key=self.config.api_key,
            base_url=writer_base_url,
        )

        self.reviewer_model = ChatOpenAI(
            model=reviewer_model_name,
            temperature=0.3,
            api_key=self.config.api_key,
            base_url=reviewer_base_url,
        )
        
        # 创建 Supervisor
        self.supervisor = TestCaseSupervisor(
            reader_model=self.reader_model,
            writer_model=self.writer_model,
            reviewer_model=self.reviewer_model,
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
    ) -> TestCaseState:
        """生成测试用例
        
        Args:
            requirement: 测试需求描述
            test_type: 测试类型 (API/Web/App)
            max_iterations: 最大迭代次数
            
        Returns:
            最终状态
        """
        # 创建初始状态
        state = TestCaseState(
            requirement=requirement,
            test_type=test_type,
            max_iterations=max_iterations,
        )
        
        # 运行 Supervisor
        final_state = await self.supervisor.run(state)
        
        return final_state
    
    def get_result(self, state: TestCaseState) -> dict:
        """获取生成结果
        
        Args:
            state: 最终状态
            
        Returns:
            结果字典
        """
        return {
            "requirement": state.requirement,
            "test_type": state.test_type,
            "analysis": state.analysis,
            "test_points": state.test_points,
            "testcases": state.testcases,
            "review": state.review,
            "iteration": state.iteration,
            "completed": state.completed,
        }


# 创建全局生成器实例 (供外部导入使用)
generator = TestCaseGeneratorV3(
    enable_middleware=True,  # 启用 middlewareV1
    enable_human_review=False,  # 默认关闭人工审核
    enable_persistence=True,  # 启用持久化
)

