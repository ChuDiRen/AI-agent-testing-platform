"""Supervisor 协调者 - 调度4个专家智能体"""
from typing import Literal, Optional

from langchain_core.language_models import BaseChatModel

from .agents import (
    create_analyzer_agent,
    create_test_point_designer_agent,
    create_writer_agent,
    create_reviewer_agent,
)
from .agents.analyzer_agent import run_analyzer
from .agents.reviewer_agent import run_reviewer
from .agents.test_point_designer_agent import run_test_point_designer
from .agents.writer_agent import WriterProgressHook, run_writer
from .database import TestCaseDB
from .models import TestCaseState


class TestCaseSupervisor:
    """测试用例生成 Supervisor - 协调4个专家智能体
    
    工作流程:
    1. Analyzer: 分析需求 → analysis
    2. TestPointDesigner: 设计测试点 → test_points
    3. Writer: 编写用例 → testcases
    4. Reviewer: 评审用例 → review
    5. 如果评审不通过且未达到最大迭代次数,返回步骤3
    """
    
    def __init__(
        self,
        reader_model: BaseChatModel,
        writer_model: BaseChatModel,
        reviewer_model: BaseChatModel,
        enable_middleware: bool = True,
        enable_human_review: bool = False,
        enable_persistence: bool = True,
        db_path: Optional[str] = None,
        writer_status_hook: Optional[WriterProgressHook] = None,
    ):
        """初始化 Supervisor

        Args:
            reader_model: 需求分析和测试点设计使用的模型
            writer_model: 用例编写使用的模型
            reviewer_model: 用例评审使用的模型
            enable_middleware: 是否启用 middlewareV1
            enable_human_review: 是否启用人工审核
            enable_persistence: 是否启用持久化存储
            db_path: 数据库路径
        """
        self.reader_model = reader_model
        self.writer_model = writer_model
        self.reviewer_model = reviewer_model
        self.enable_middleware = enable_middleware
        self.enable_human_review = enable_human_review
        self.enable_persistence = enable_persistence

        # 创建4个专家智能体
        self.analyzer = create_analyzer_agent(reader_model)
        self.test_point_designer = create_test_point_designer_agent(reader_model)
        self.writer = create_writer_agent(writer_model)
        self.reviewer = create_reviewer_agent(reviewer_model)

        # 初始化数据库 (如果启用持久化)
        if enable_persistence:
            from pathlib import Path
            self.db = TestCaseDB(Path(db_path) if db_path else Path(__file__).parent / "testcases.db")
        else:
            self.db = None
        self.writer_status_hook = writer_status_hook
    
    async def run(self, state: TestCaseState, writer_status_hook: Optional[WriterProgressHook] = None) -> TestCaseState:
        """运行完整的测试用例生成流程

        Args:
            state: 初始状态

        Returns:
            最终状态
        """
        import asyncio
        import time
        run_start = time.time()
        extra_hooks = [hook for hook in (self.writer_status_hook, writer_status_hook) if hook]
        
        async def writer_progress_hook(chunk_updates):
            """Writer chunk 进度回调"""
            for key, value in chunk_updates.items():
                setattr(state, key, value)
            if self.db:
                self.db.save_testcase(state)
            for hook in extra_hooks:
                await hook(chunk_updates)

        # 1️⃣ + 2️⃣ 并行执行: Analyzer 和 TestPointDesigner (无依赖关系)
        if not state.analyze_completed and not state.design_completed:
            print("\n[1/4] 需求分析与测试点设计...")
            
            # 并行执行两个agent
            analyzer_task = run_analyzer(self.analyzer, state, enable_middleware=self.enable_middleware)
            designer_task = run_test_point_designer(self.test_point_designer, state, enable_middleware=self.enable_middleware)
            
            # 使用asyncio.gather并行等待
            analyzer_updates, designer_updates = await asyncio.gather(
                analyzer_task,
                designer_task,
                return_exceptions=True
            )
            
            # 检查是否有异常
            if isinstance(analyzer_updates, Exception):
                print(f"❌ 需求分析失败: {analyzer_updates}")
                raise analyzer_updates
            if isinstance(designer_updates, Exception):
                print(f"❌ 测试点设计失败: {designer_updates}")
                raise designer_updates
            
            # 合并更新
            for key, value in analyzer_updates.items():
                setattr(state, key, value)
            for key, value in designer_updates.items():
                setattr(state, key, value)
            
            print("✅ 需求分析与测试点设计完成")
            
            # 保存到数据库
            if self.db:
                self.db.save_testcase(state)
        
        # 如果只有其中一个未完成,则顺序执行
        elif not state.analyze_completed:
            print("\
[1/4] 需求分析...")
            updates = await run_analyzer(self.analyzer, state, enable_middleware=self.enable_middleware)
            for key, value in updates.items():
                setattr(state, key, value)
            print("✅ 需求分析完成")

            # 保存到数据库
            if self.db:
                self.db.save_testcase(state)

        elif not state.design_completed:
            print("\
[2/4] 测试点设计...")
            updates = await run_test_point_designer(self.test_point_designer, state, enable_middleware=self.enable_middleware)
            for key, value in updates.items():
                setattr(state, key, value)
            print("✅ 测试点设计完成")

            # 保存到数据库
            if self.db:
                self.db.save_testcase(state)

        # 3️⃣ 用例编写 (可能多次迭代)
        while state.iteration < state.max_iterations:
            # 编写用例
            print(f"\
[3/4] 编写测试用例 (第{state.iteration + 1}轮)...")
            updates = await run_writer(
                self.writer,
                state,
                enable_middleware=self.enable_middleware,
                enable_human_review=self.enable_human_review,
                progress_hook=writer_progress_hook,
            )

            # 如果人工审核未通过,跳过
            if not updates:
                print("⏭️  跳过此次生成")
                break

            for key, value in updates.items():
                setattr(state, key, value)
            print("✅ 测试用例编写完成")

            # 保存到数据库
            if self.db:
                self.db.save_testcase(state)

            # 评审用例
            print(f"\
[4/4] 评审测试用例...")
            updates = await run_reviewer(self.reviewer, state, enable_middleware=self.enable_middleware)
            for key, value in updates.items():
                setattr(state, key, value)
            print("✅ 评审完成")

            # 保存到数据库
            if self.db:
                self.db.save_testcase(state)

            # 检查是否通过评审
            if "通过" in state.review or "PASS" in state.review.upper():
                print("\
✅ 评审通过,测试用例生成完成!")
                break
            elif state.iteration >= state.max_iterations:
                print(f"\
⚠️  已达到最大迭代次数({state.max_iterations}),停止迭代")
                break
            else:
                print(f"\
🔄 评审未通过,进入第{state.iteration + 1}轮优化...")
                # 重置生成完成标记,允许重新生成
                state.generate_completed = False

        # 最终保存
        if self.db:
            self.db.save_testcase(state)

        total_elapsed = time.time() - run_start
        print(f"\
✅ 全部完成! 总耗时: {total_elapsed:.1f}秒")

        return state
    
    def decide_next_step(self, state: TestCaseState) -> Literal["analyze", "design", "write", "review", "end"]:
        """决定下一步执行哪个智能体
        
        Args:
            state: 当前状态
            
        Returns:
            下一步动作
        """
        if not state.analyze_completed:
            return "analyze"
        elif not state.design_completed:
            return "design"
        elif not state.generate_completed or (state.review and "通过" not in state.review and state.iteration < state.max_iterations):
            return "write"
        elif not state.review_completed or state.iteration < state.max_iterations:
            return "review"
        else:
            return "end"
