"""
TestCaseSupervisor - 监督者

协调各专家智能体的执行顺序，管理迭代流程
"""
import logging
from datetime import datetime
from typing import Optional, Callable
from langchain_openai import ChatOpenAI

from .state import TestCaseState, GenerationStage
from .agents import AnalyzerAgent, TestPointDesignerAgent, WriterAgent, ReviewerAgent
from .agents.base import ProgressCallback

logger = logging.getLogger(__name__)


class TestCaseSupervisor:
    """测试用例生成监督者"""

    def __init__(
        self,
        reader_model: ChatOpenAI,
        writer_model: ChatOpenAI,
        reviewer_model: ChatOpenAI,
        progress_callback: Optional[ProgressCallback] = None,
    ):
        self.progress_callback = progress_callback
        # 初始化各智能体
        self.analyzer = AnalyzerAgent(reader_model, progress_callback)
        self.designer = TestPointDesignerAgent(reader_model, progress_callback)
        self.writer = WriterAgent(writer_model, progress_callback)
        self.reviewer = ReviewerAgent(reviewer_model, progress_callback)

    def emit_progress(self, stage: str, message: str, progress: float = 0.0):
        """发送进度事件"""
        if self.progress_callback:
            self.progress_callback(stage, message, progress)

    async def run(self, state: TestCaseState) -> TestCaseState:
        """执行完整的生成流程"""
        state.start_time = datetime.now()
        logger.info(f"Starting generation for: {state.requirement[:50]}...")
        try:
            # 1. 需求分析
            self.emit_progress("supervisor", "开始需求分析...", 0.0)
            state = await self.analyzer.run(state)
            if state.error:
                return self._finalize(state)
            # 2. 测试点设计
            self.emit_progress("supervisor", "开始测试点设计...", 25.0)
            state = await self.designer.run(state)
            if state.error:
                return self._finalize(state)
            # 3. 用例编写和评审循环
            while not state.completed and state.iteration < state.max_iterations:
                # 编写用例
                self.emit_progress("supervisor", f"开始编写用例 (迭代 {state.iteration + 1})...", 50.0)
                state = await self.writer.run(state)
                if state.error:
                    return self._finalize(state)
                # 评审用例
                self.emit_progress("supervisor", "开始用例评审...", 75.0)
                state = await self.reviewer.run(state)
                if state.error:
                    return self._finalize(state)
                if not state.completed:
                    logger.info(f"Quality score {state.quality_score} < 80, retrying...")
            self.emit_progress("supervisor", "生成完成", 100.0)
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            state.error = str(e)
            state.stage = GenerationStage.FAILED
        return self._finalize(state)


    def _finalize(self, state: TestCaseState) -> TestCaseState:
        """完成处理"""
        state.end_time = datetime.now()
        if state.error:
            state.stage = GenerationStage.FAILED
        elif state.completed:
            state.stage = GenerationStage.COMPLETED
        logger.info(
            f"Generation finished: stage={state.stage.value}, "
            f"score={state.quality_score}, iterations={state.iteration}, "
            f"duration={state.get_duration_seconds():.2f}s"
        )
        return state
