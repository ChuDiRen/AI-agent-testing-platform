"""Supervisor 协调者 - 调度5个专家智能体

核心特性:
1. 智能意图识别: 根据用户输入自动识别目标阶段
2. 完成标志检测: 通过标志精确识别每个阶段的完成情况
3. 智能Token管理: 分层过滤策略，大幅降低Token消耗
4. 流程自动推进: 看到完成标志后自动调用下一个专家
5. 评审-修改循环: 支持最多3次迭代优化
"""
import re
from typing import Literal, Optional, Dict, Any, List
from enum import Enum

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

from .agents import (
    create_analyzer_agent,
    create_test_point_designer_agent,
    create_writer_agent,
    create_reviewer_agent,
    run_tool_agent,
)
from .agents.analyzer_agent import run_analyzer
from .agents.reviewer_agent import run_reviewer
from .agents.test_point_designer_agent import run_test_point_designer
from .agents.writer_agent import WriterProgressHook, run_writer
from .database import TestCaseDB
from .models import TestCaseState


# ============== 完成标志定义 ==============

class CompletionFlag(Enum):
    """完成标志枚举"""
    ANALYZE_COMPLETED = "需求分析完成"
    DESIGN_COMPLETED = "测试点设计完成"
    GENERATE_COMPLETED = "测试用例设计完成"
    REVIEW_PASSED = "测试用例评审完成"
    REVIEW_FAILED = "需要重新设计"
    PROCESS_COMPLETED = "所有处理步骤已完成"


# ============== 意图识别 ==============

class IntentRecognizer:
    """意图识别器 - 识别用户想要什么"""
    
    # 意图关键词映射
    INTENT_KEYWORDS = {
        "analyze": ["分析", "理解", "解析", "需求分析"],
        "design": ["设计", "测试点", "覆盖"],
        "generate": ["生成", "编写", "用例", "测试用例"],
        "full": ["完整", "全部", "所有", "全流程"],
    }
    
    @staticmethod
    def recognize(user_input: str) -> str:
        """识别用户意图
        
        Args:
            user_input: 用户输入
            
        Returns:
            目标阶段: analyze/design/generate/end
        """
        user_input_lower = user_input.lower()
        
        # 检查是否只要分析
        if any(kw in user_input_lower for kw in IntentRecognizer.INTENT_KEYWORDS["analyze"]):
            if not any(kw in user_input_lower for kw in IntentRecognizer.INTENT_KEYWORDS["generate"]):
                return "analyze"
        
        # 检查是否只要测试点设计
        if any(kw in user_input_lower for kw in IntentRecognizer.INTENT_KEYWORDS["design"]):
            if not any(kw in user_input_lower for kw in IntentRecognizer.INTENT_KEYWORDS["generate"]):
                return "design"
        
        # 默认完整流程
        return "end"


# ============== Token管理 ==============

class TokenManager:
    """智能Token管理器 - 优化上下文，降低成本"""
    
    # Supervisor专属过滤策略
    SUPERVISOR_FILTER = {
        "human": 5,    # 保留5条HumanMessage
        "ai": 5,       # 保留5条AIMessage
        "system": 1,   # 保留1条SystemMessage
        "tool": 0,     # 不保留ToolMessage
    }
    
    # 子智能体过滤策略
    AGENT_FILTER = {
        "human": 3,
        "ai": 3,
        "system": 1,
        "tool": 5,
    }
    
    @staticmethod
    def filter_messages(
        messages: List,
        strategy: Dict[str, int],
        phase_name: str = ""
    ) -> List:
        """过滤消息历史
        
        Args:
            messages: 消息列表
            strategy: 过滤策略
            phase_name: 阶段名称 (用于日志)
            
        Returns:
            过滤后的消息列表
        """
        if not messages:
            return []
        
        # 按类型分组
        human_msgs = []
        ai_msgs = []
        system_msgs = []
        tool_msgs = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                human_msgs.append(msg)
            elif isinstance(msg, AIMessage):
                ai_msgs.append(msg)
            elif isinstance(msg, SystemMessage):
                system_msgs.append(msg)
            elif isinstance(msg, ToolMessage):
                tool_msgs.append(msg)
        
        # 按策略保留
        filtered = []
        
        # SystemMessage 放在最前面
        if strategy.get("system", 0) > 0 and system_msgs:
            filtered.extend(system_msgs[-strategy["system"]:])
        
        # 保留最新的Human和AI消息
        if strategy.get("human", 0) > 0:
            filtered.extend(human_msgs[-strategy["human"]:])
        if strategy.get("ai", 0) > 0:
            filtered.extend(ai_msgs[-strategy["ai"]:])
        if strategy.get("tool", 0) > 0:
            filtered.extend(tool_msgs[-strategy["tool"]:])
        
        return filtered
    
    @staticmethod
    def estimate_tokens(messages: List) -> int:
        """估算消息的Token数量 (粗略估计)"""
        total_chars = sum(len(str(msg.content)) for msg in messages if hasattr(msg, 'content'))
        # 中文约1.5字符/token，英文约4字符/token，取平均
        return int(total_chars / 2.5)


class TestCaseSupervisor:
    """测试用例生成 Supervisor - 协调5个专家智能体
    
    工作流程:
    1. Analyzer: 分析需求 → analysis (需求分析完成)
    2. TestPointDesigner: 设计测试点 → test_points (测试点设计完成)
    3. Writer: 编写用例 → testcases (测试用例设计完成)
    4. Reviewer: 评审用例 → review (测试用例评审完成/需要重新设计)
    5. ToolAgent: 数据处理 → xmind/excel (所有处理步骤已完成)
    
    完成标志机制:
    - 每个阶段输出特定的完成标志
    - Supervisor通过检测标志来决定下一步
    - 支持评审-修改循环 (最多3次)
    """
    
    def __init__(
        self,
        reader_model: BaseChatModel,
        writer_model: BaseChatModel,
        reviewer_model: BaseChatModel,
        enable_middleware: bool = True,
        enable_human_review: bool = False,
        enable_persistence: bool = True,
        enable_data_export: bool = True,
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
            enable_data_export: 是否启用数据导出 (XMind/Excel)
            db_path: 数据库路径
        """
        self.reader_model = reader_model
        self.writer_model = writer_model
        self.reviewer_model = reviewer_model
        self.enable_middleware = enable_middleware
        self.enable_human_review = enable_human_review
        self.enable_persistence = enable_persistence
        self.enable_data_export = enable_data_export

        # 创建4个LLM专家智能体
        self.analyzer = create_analyzer_agent(reader_model)
        self.test_point_designer = create_test_point_designer_agent(reader_model)
        self.writer = create_writer_agent(writer_model)
        self.reviewer = create_reviewer_agent(reviewer_model)
        
        # 数据处理专家不需要LLM，是自定义节点
        # 测试方法选择已集成到 Writer 智能体中（工具函数，不消耗Token）

        # 初始化数据库 (如果启用持久化)
        if enable_persistence:
            from pathlib import Path
            self.db = TestCaseDB(Path(db_path) if db_path else Path(__file__).parent.parent.parent / "data" / "testcases.db")
        else:
            self.db = None
        self.writer_status_hook = writer_status_hook
        
        # 意图识别器
        self.intent_recognizer = IntentRecognizer()
        
        # Token管理器
        self.token_manager = TokenManager()
    
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
        
        # 识别用户意图，确定目标阶段
        target_phase = self.intent_recognizer.recognize(state.requirement)
        state.target_phase = target_phase
        print(f"\n🎯 识别到目标阶段: {target_phase}")
        
        async def writer_progress_hook(chunk_updates):
            """Writer chunk 进度回调"""
            for key, value in chunk_updates.items():
                setattr(state, key, value)
            if self.db:
                self.db.save_testcase(state)
            for hook in extra_hooks:
                await hook(chunk_updates)

        # ============== 阶段1+2: 需求分析与测试点设计 (并行) ==============
        if not state.analyze_completed and not state.design_completed:
            print("\n[1/5] 需求分析专家 + 测试点设计专家 (并行执行)...")
            
            # Token优化: 过滤消息历史
            if self.enable_middleware:
                original_count = len(state.messages)
                state.messages = self.token_manager.filter_messages(
                    state.messages, 
                    TokenManager.SUPERVISOR_FILTER,
                    "supervisor"
                )
                if original_count > 0:
                    print(f"  📉 Token优化: {original_count} → {len(state.messages)} 条消息")
            
            # 并行执行两个agent
            analyzer_task = run_analyzer(self.analyzer, state, enable_middleware=self.enable_middleware)
            designer_task = run_test_point_designer(self.test_point_designer, state, enable_middleware=self.enable_middleware)
            
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
            
            # 检测完成标志
            if self._check_completion_flag(state.analysis, CompletionFlag.ANALYZE_COMPLETED):
                print(f"  ✅ 检测到完成标志: {CompletionFlag.ANALYZE_COMPLETED.value}")
            if self._check_completion_flag(state.test_points, CompletionFlag.DESIGN_COMPLETED):
                print(f"  ✅ 检测到完成标志: {CompletionFlag.DESIGN_COMPLETED.value}")
            
            print("✅ 需求分析与测试点设计完成")
            
            # 保存到数据库
            if self.db:
                self.db.save_testcase(state)
            
            # 如果目标只是分析，到此结束
            if target_phase == "analyze":
                print("\n🎯 已达到目标阶段: 需求分析")
                return state
        
        # 如果只有其中一个未完成,则顺序执行
        elif not state.analyze_completed:
            print("\n[1/5] 需求分析专家...")
            updates = await run_analyzer(self.analyzer, state, enable_middleware=self.enable_middleware)
            for key, value in updates.items():
                setattr(state, key, value)
            print("✅ 需求分析完成")
            if self.db:
                self.db.save_testcase(state)
            
            if target_phase == "analyze":
                return state

        elif not state.design_completed:
            print("\n[2/5] 测试点设计专家...")
            updates = await run_test_point_designer(self.test_point_designer, state, enable_middleware=self.enable_middleware)
            for key, value in updates.items():
                setattr(state, key, value)
            print("✅ 测试点设计完成")
            if self.db:
                self.db.save_testcase(state)
        
        # 如果目标只是设计，到此结束
        if target_phase == "design":
            print("\n🎯 已达到目标阶段: 测试点设计")
            return state

        # ============== 阶段3+4: 用例编写与评审 (迭代循环) ==============
        # 测试方法选择已集成到 Writer 智能体中（工具函数，不消耗Token）
        while state.iteration < state.max_iterations:
            # 编写用例（Writer 内部会自动选择测试方法并注入模板）
            print(f"\n[3/5] 测试用例编写专家 (第{state.iteration + 1}轮)...")
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
            
            # 保存版本历史
            state.add_test_case_version(state.testcases, state.quality_score)
            print("✅ 测试用例编写完成")

            # 保存到数据库
            if self.db:
                self.db.save_testcase(state)

            # 评审用例
            print(f"\n[4/5] 测试用例评审专家...")
            updates = await run_reviewer(self.reviewer, state, enable_middleware=self.enable_middleware)
            for key, value in updates.items():
                setattr(state, key, value)
            
            # 使用评审专家返回的质量评分 (已在run_reviewer中解析)
            quality_score = state.quality_score
            
            # 保存评审历史
            review_passed = quality_score >= 80.0 or "通过" in state.review or "PASS" in state.review.upper()
            state.add_review_record(
                feedback=state.review,
                score=quality_score,
                passed=review_passed,
                dimensions=state.quality_dimensions
            )
            
            print(f"✅ 评审完成 (质量评分: {quality_score:.1f}分)")

            # 保存到数据库
            if self.db:
                self.db.save_testcase(state)

            # 检查是否通过评审
            if review_passed:
                print("\n✅ 评审通过,测试用例生成完成!")
                break
            elif state.iteration >= state.max_iterations:
                print(f"\n⚠️  已达到最大迭代次数({state.max_iterations}),停止迭代")
                break
            else:
                # 注意: 此时iteration已经在run_reviewer中被+1了
                # 所以state.iteration就是下一轮的轮次
                print(f"\n🔄 评审未通过 (评分: {quality_score:.1f}),进入第{state.iteration + 1}轮优化...")
                # 重置生成完成标记,允许重新生成
                state.generate_completed = False

        # ============== 阶段5: 数据处理 (导出XMind/Excel) ==============
        if self.enable_data_export and state.testcases:
            print("\n[5/5] 数据处理专家...")
            try:
                updates = await run_tool_agent(state)
                for key, value in updates.items():
                    setattr(state, key, value)
                
                # 输出下载链接
                if state.xmind_path:
                    print(f"  📊 XMind思维导图: {state.xmind_path}")
                if state.excel_path:
                    print(f"  📋 Excel测试用例: {state.excel_path}")
                if state.statistics:
                    print(f"  📈 统计信息: 共{state.statistics.get('总用例数', 0)}个用例")
                    
            except Exception as e:
                print(f"⚠️ 数据处理失败: {e}")

        # 最终保存
        if self.db:
            self.db.save_testcase(state)

        total_elapsed = time.time() - run_start
        print(f"\n✅ 全部完成! 总耗时: {total_elapsed:.1f}秒")

        return state
    
    def _check_completion_flag(self, text: str, flag: CompletionFlag) -> bool:
        """检查文本中是否包含完成标志
        
        Args:
            text: 要检查的文本
            flag: 完成标志
            
        Returns:
            是否包含标志
        """
        if not text:
            return False
        return flag.value in text
    
    def _extract_quality_score(self, review_text: str) -> float:
        """从评审文本中提取质量评分
        
        Args:
            review_text: 评审文本
            
        Returns:
            质量评分 (0-100)
        """
        if not review_text:
            return 0.0
        
        # 尝试匹配各种评分格式
        patterns = [
            r'总分[：:]\s*(\d+(?:\.\d+)?)',
            r'评分[：:]\s*(\d+(?:\.\d+)?)',
            r'质量评分[：:]\s*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*分',
            r'得分[：:]\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, review_text)
            if match:
                score = float(match.group(1))
                if 0 <= score <= 100:
                    return score
        
        # 如果找不到评分，根据关键词估算
        if "通过" in review_text or "PASS" in review_text.upper():
            return 85.0
        elif "不通过" in review_text or "FAIL" in review_text.upper():
            return 60.0
        
        return 70.0  # 默认分数
    
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
