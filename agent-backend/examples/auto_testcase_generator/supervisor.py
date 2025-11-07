"""Supervisor 协调者 - 调度4个专家智能体"""
from typing import Literal, Optional
from langchain_core.language_models import BaseChatModel
from .models import TestCaseState
from .agents import (
    create_analyzer_agent,
    create_test_point_designer_agent,
    create_writer_agent,
    create_reviewer_agent,
)
from .agents.analyzer_agent import run_analyzer
from .agents.test_point_designer_agent import run_test_point_designer
from .agents.writer_agent import run_writer
from .agents.reviewer_agent import run_reviewer
from .database import TestCaseDB


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
    
    async def run(self, state: TestCaseState) -> TestCaseState:
        """运行完整的测试用例生成流程

        Args:
            state: 初始状态

        Returns:
            最终状态
        """
        # 1️⃣ 需求分析
        if not state.analyze_completed:
            print(f"\n{'='*60}")
            print(f"🔍 [Analyzer] 开始分析需求... (middlewareV1: {'✅' if self.enable_middleware else '❌'})")
            print(f"{'='*60}")
            updates = await run_analyzer(self.analyzer, state, enable_middleware=self.enable_middleware)
            for key, value in updates.items():
                setattr(state, key, value)
            print(f"✅ [Analyzer] 需求分析完成")

            # 保存到数据库
            if self.db:
                self.db.save_testcase(state)

        # 2️⃣ 测试点设计
        if not state.design_completed:
            print(f"\n{'='*60}")
            print(f"📋 [TestPointDesigner] 开始设计测试点... (middlewareV1: {'✅' if self.enable_middleware else '❌'})")
            print(f"{'='*60}")
            updates = await run_test_point_designer(self.test_point_designer, state, enable_middleware=self.enable_middleware)
            for key, value in updates.items():
                setattr(state, key, value)
            print(f"✅ [TestPointDesigner] 测试点设计完成")

            # 保存到数据库
            if self.db:
                self.db.save_testcase(state)

        # 3️⃣ 用例编写 (可能多次迭代)
        while state.iteration < state.max_iterations:
            # 编写用例
            print(f"\n{'='*60}")
            print(f"✍️  [Writer] 开始编写测试用例 (第{state.iteration + 1}轮)... (middlewareV1: {'✅' if self.enable_middleware else '❌'}, 人工审核: {'✅' if self.enable_human_review else '❌'})")
            print(f"{'='*60}")
            updates = await run_writer(
                self.writer,
                state,
                enable_middleware=self.enable_middleware,
                enable_human_review=self.enable_human_review
            )

            # 如果人工审核未通过,跳过
            if not updates:
                print("⏭️  跳过此次生成")
                break

            for key, value in updates.items():
                setattr(state, key, value)
            print(f"✅ [Writer] 测试用例编写完成")

            # 保存到数据库
            if self.db:
                self.db.save_testcase(state)

            # 评审用例
            print(f"\n{'='*60}")
            print(f"🔎 [Reviewer] 开始评审测试用例... (middlewareV1: {'✅' if self.enable_middleware else '❌'})")
            print(f"{'='*60}")
            updates = await run_reviewer(self.reviewer, state, enable_middleware=self.enable_middleware)
            for key, value in updates.items():
                setattr(state, key, value)
            print(f"✅ [Reviewer] 评审完成")

            # 保存到数据库
            if self.db:
                self.db.save_testcase(state)

            # 检查是否通过评审
            if "通过" in state.review or "PASS" in state.review.upper():
                print(f"\n🎉 评审通过!测试用例生成完成!")
                break
            elif state.iteration >= state.max_iterations:
                print(f"\n⚠️  已达到最大迭代次数({state.max_iterations}),停止迭代")
                break
            else:
                print(f"\n🔄 评审未通过,准备第{state.iteration + 1}轮优化...")
                # 重置生成完成标记,允许重新生成
                state.generate_completed = False

        # 最终保存
        if self.db:
            self.db.save_testcase(state)

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

