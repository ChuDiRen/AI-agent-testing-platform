"""
TestCaseGenerator - 测试用例生成器

核心生成引擎，支持单个和批量生成
"""
import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, List, Callable, Any, Dict

from .state import TestCaseState
from .supervisor import TestCaseSupervisor
from .services import ModelService, CacheService, ContextCompressor
from .agents.base import ProgressCallback, ErrorCallback

logger = logging.getLogger(__name__)


@dataclass
class GeneratorConfig:
    """生成器配置"""
    api_key: str
    provider: str = "siliconflow"
    reader_model: str = "deepseek-ai/DeepSeek-V3"
    writer_model: str = "deepseek-ai/DeepSeek-V3"
    reviewer_model: str = "deepseek-ai/DeepSeek-V3"
    enable_cache: bool = True
    enable_compression: bool = True


class TestCaseGenerator:
    """测试用例生成器"""

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.cache = CacheService() if config.enable_cache else None
        # 创建模型实例
        self.reader_model = ModelService.create_chat_model(
            config.provider, config.reader_model, config.api_key, temperature=0.3
        )
        self.writer_model = ModelService.create_chat_model(
            config.provider, config.writer_model, config.api_key, temperature=0.7
        )
        self.reviewer_model = ModelService.create_chat_model(
            config.provider, config.reviewer_model, config.api_key, temperature=0.1
        )
        # 上下文压缩器
        self.compressor = ContextCompressor(self.reader_model) if config.enable_compression else None

    async def generate(
        self,
        requirement: str,
        test_type: str = "API",
        max_iterations: int = 2,
        progress_callback: Optional[ProgressCallback] = None,
        error_callback: Optional[ErrorCallback] = None,
        db_session = None,
    ) -> TestCaseState:
        """生成测试用例"""
        logger.info(f"Generating test cases for: {requirement[:50]}...")
        # 检查缓存
        if self.cache:
            cache_key = self.cache._generate_key(requirement, test_type)
            cached = self.cache.get(cache_key)
            if cached:
                logger.info("Cache hit, returning cached result")
                return TestCaseState.from_dict(cached)
        # 创建状态
        state = TestCaseState(
            requirement=requirement,
            test_type=test_type,
            max_iterations=max_iterations,
        )
        # 创建Supervisor并执行
        supervisor = TestCaseSupervisor(
            reader_model=self.reader_model,
            writer_model=self.writer_model,
            reviewer_model=self.reviewer_model,
            progress_callback=progress_callback,
            error_callback=error_callback,
            db_session=db_session,
            test_type=test_type,
        )
        state = await supervisor.run(state)
        # 缓存结果
        if self.cache and state.completed:
            self.cache.set(cache_key, state.to_dict())
        return state


    async def batch_generate(
        self,
        requirements: List[str],
        test_type: str = "API",
        max_concurrent: int = 5,
        max_iterations: int = 2,
        progress_callback: Optional[Callable[[int, int, TestCaseState], None]] = None,
    ) -> List[TestCaseState]:
        """批量并行生成"""
        logger.info(f"Batch generating {len(requirements)} test cases, max_concurrent={max_concurrent}")
        semaphore = asyncio.Semaphore(max_concurrent)
        results: List[TestCaseState] = []

        async def generate_one(index: int, req: str) -> TestCaseState:
            async with semaphore:
                state = await self.generate(req, test_type, max_iterations)
                if progress_callback:
                    progress_callback(index, len(requirements), state)
                return state

        tasks = [generate_one(i, req) for i, req in enumerate(requirements)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # 处理异常
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                state = TestCaseState(requirement=requirements[i], test_type=test_type)
                state.error = str(result)
                final_results.append(state)
            else:
                final_results.append(result)
        logger.info(f"Batch generation completed: {len(final_results)} results")
        return final_results

    def get_statistics(self, states: List[TestCaseState]) -> Dict[str, Any]:
        """获取批量生成统计"""
        total = len(states)
        completed = sum(1 for s in states if s.completed)
        failed = sum(1 for s in states if s.error)
        total_tokens = sum(s.get_total_tokens() for s in states)
        total_duration = sum(s.get_duration_seconds() for s in states)
        avg_score = sum(s.quality_score for s in states) / total if total > 0 else 0

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total if total > 0 else 0,
            "total_tokens": total_tokens,
            "total_duration_seconds": total_duration,
            "average_score": avg_score,
        }
